import threading
import logging
from typing import Callable, Optional

import websocket  # websocket-client


class SocketWS:
    """
    WebSocket class.

    - connect() establishes a WebSocket handshake
    - listen(cb) registers a callback and starts a background receive loop
    - send(msg) sends a text frame
    - receive loop delivers raw text messages (strings) to the callback
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 1111, path: str = ""):
        """
        host: should include scheme ws:// or wss://
              e.g., "ws://127.0.0.1" or "ws://192.168.1.5"
        port: websocket server port
        path: optional, e.g. "/ws" (leave "" for the server)
        """
        self.logger = logging.getLogger("Socket")
        logging.basicConfig(level=logging.INFO)

        self.host = host.rstrip("/")
        if self.host and not self.host.startswith("ws://") and not self.host.startswith("wss://"):
            self.host = "ws://" + self.host
        self.port = port
        self.path = path

        self._on_message: Optional[Callable[[str], None]] = None
        self._wsapp: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._connected_event = threading.Event()

        self.connect()

    def _build_url(self) -> str:
        if self.path:
            return f"{self.host}:{self.port}/{self.path.lstrip('/')}"
        return f"{self.host}:{self.port}"

    def connect(self):
        """
        Establish a WebSocket connection (handshake). Starts the WebSocketApp loop in a thread.
        """
        url = self._build_url()

        def on_open(ws):
            self._connected_event.set()
            self.logger.info(f"✅ Connected (WebSocket) to {url}")

        def on_message(ws, message: str):
            self.logger.info(f"[RECV] {message}")
            if self._on_message:
                try:
                    self._on_message(message)
                except Exception as e:
                    self.logger.error(f"Error in on_message callback: {e}")

        def on_error(ws, error):
            # connection errors show here
            self.logger.error(f"❌ WebSocket error: {error}")

        def on_close(ws, status_code, msg):
            self._connected_event.clear()
            self.logger.info(f"🔌 WebSocket closed. code={status_code}, reason={msg}")

        self._wsapp = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Run WebSocket receive loop in a background thread
        self._thread = threading.Thread(
            target=self._wsapp.run_forever,
            kwargs={"ping_interval": 30, "ping_timeout": 10},
            daemon=True
        )
        self._thread.start()

        # Optional: wait briefly for connection to establish
        if not self._connected_event.wait(timeout=5):
            self.logger.error(f"❌ Failed to connect (timeout) to {url}")

    def send(self, message: str):
        """
        Send a text message over WebSocket.
        """
        try:
            if not self._wsapp or not self._connected_event.is_set():
                raise RuntimeError("WebSocket is not connected.")
            self._wsapp.send(message)
            self.logger.info(f"[SEND] {message}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    def listen(self, on_message: Callable[[str], None]):
        """
        Register a callback for incoming messages.
        WebSocketApp already listens in its own thread; this just sets the handler.
        """
        self._on_message = on_message

    def close(self):
        """
        Close the WebSocket connection.
        """
        try:
            if self._wsapp:
                self._wsapp.close()
            self._connected_event.clear()
            self.logger.info("🔌 WebSocket connection closed.")
        except Exception as e:
            self.logger.error(f"Error closing WebSocket: {e}")
