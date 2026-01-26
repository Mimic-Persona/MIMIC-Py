import socket
import threading
import logging


class SocketTCP:
    def __init__(self, host: str = "127.0.0.1", port: int = 1111):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger = logging.getLogger("SocketTCP")
        logging.basicConfig(level=logging.INFO)
        self._listener_thread = None
        self._on_message = None
        self._buffer = ""
        self.connect()

    def connect(self):
        """
        Establish a connection to the specified host and port.
        :return: None
        """
        try:
            self.sock.connect((self.host, self.port))
            self.logger.info(f"✅ Connected to {self.host}:{self.port}")
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to {self.host}:{self.port}: {e}")

    def send(self, message: str):
        """
        Send a message to the connected socket.
        :param message: The message to send.
        :return: None
        """
        try:
            self.sock.sendall((message + "\n").encode("utf-8"))
            self.logger.info(f"[SEND] {message}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    def receive(self) -> str:
        """
        Receive a message from the connected socket.
        :return: The received message as a string.
        """
        while "\n" not in self._buffer:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                self._buffer += data.decode("utf-8")
            except Exception as e:
                self.logger.error(f"Error receiving message: {e}")
                return ""
        if "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            return line
        return ""

    def listen(self, on_message):
        """
        Start listening for incoming messages and call the provided callback function when a message is received.
        :param on_message: A callback function that takes a message as an argument.
        :return: None
        """
        self._on_message = on_message
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._listener_thread.start()

    def _listen_loop(self):
        """
        Continuously listen for incoming messages and call the on_message callback.
        :return: None
        """
        while True:
            message = self.receive()
            if message and self._on_message:
                self._on_message(message)

    def close(self):
        """
        Close the socket connection.
        :return: None
        """
        try:
            self.sock.close()
            self.logger.info("🔌 Socket connection closed.")
        except Exception as e:
            self.logger.error(f"Error closing socket: {e}")
