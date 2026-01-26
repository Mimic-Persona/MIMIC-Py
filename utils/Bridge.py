import json
import os
import threading
import time

from typing import Any, Optional, Union
from dotenv import load_dotenv

from MIMIC_Minecraft.mc_env.MineEnv import MineEnv
from action_executor.Feedback import Feedback
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from utils.SocketTCP import SocketTCP
from utils.SocketWS import SocketWS
from utils.types import Executor


class Bridge(BotComponent):
    def __init__(
            self,
            socket: Union[SocketTCP, SocketWS] = None,
            mine_env: MineEnv = None,
            timeout: float = 10.0,
            code_timeout: float = 600000.0
    ):
        load_dotenv()
        self.game_subject = os.getenv("GAME_SUBJECT", "SPD")
        self.report_prefix = os.getenv("AGENT_NAME", "example")
        self._lock = threading.Lock()
        self._latest_message = None

        super().__init__(
            prompt_root_path="",
            has_llm=False
        )

        if self.game_subject == "MC":
            if mine_env is None:
                raise ValueError("MineEnv must be provided for Minecraft game subject.")
            self.mine_env = mine_env

        if socket is None:
            raise ValueError("Socket must be provided for game subjects.")

        self.socket = socket
        self.socket.listen(self._on_message)

        self.timeout = timeout
        self.code_timeout = code_timeout

        self.bot_msg = f"{self.game_subject}:utils.Bridge:log:"
        self.err_msg = f"{self.game_subject}:utils.Bridge:err:"

    def _on_message(
            self,
            message: str
    ):
        """
        Callback function to handle incoming messages from the WebSocket.
        :param message: The message received from the WebSocket as a string.
        :return: None
        """
        try:
            msg = json.loads(message)
            with self._lock:
                self._latest_message = msg
                self.h(f"Message Received: {msg}")
        except json.JSONDecodeError:
            pass

    def _wait_for_msg_type(
            self,
            msg_type: str,
            timeout: float = 10.0
    ) -> Optional[dict[str, Any]]:
        """
        Waits for a message of a specific type within a timeout period.
        :param msg_type: The type of message to wait for (e.g., "status", "feedback").
        :param timeout: The maximum time to wait for the message in seconds.
        :return: The message if found, otherwise None.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self._lock:
                if self._latest_message and self._latest_message.get("msgType") == msg_type:
                    result = self._latest_message
                    self._latest_message = None  # reset after match
                    return result
            time.sleep(0.1)
        return None

    def get_command(
            self
    ) -> dict[str, Any]:
        """
        Requests the next command from the WebSocket and waits for a response.
        :return: The command message if received, otherwise None.
        """
        result = self._wait_for_msg_type("command")
        while not result:
            result = self._wait_for_msg_type("command", self.timeout)
        return result

    def get_status(
            self
    ) -> dict[str, Any]:
        """
        Requests the current status from the WebSocket and waits for a response.
        :return: The status message if received, otherwise None.
        """
        if self.game_subject != "MC":
            self.socket.send("GetStatus")
            result = self._wait_for_msg_type("status")
            while not result:
                self.socket.send(f"No status response received within {self.timeout} seconds.")
                self.socket.send("GetStatus")
                result = self._wait_for_msg_type("status", self.timeout)
            return result

        else:
            return self.mine_env.observe()

    def act_and_feedback(
            self,
            plan: Plan
    ) -> list[Feedback]:
        """
        Sends a plan to the WebSocket to execute an action and waits for feedback.
        :param plan: The plan to be executed, represented as a Plan object.
        :return: A list of Feedback objects containing feedback on the execution.
        """
        if self.game_subject == "MC":
            raise ValueError("This method is not supported for the current game subject.")

        action_msg = f"ACTION: {str(Plan.to_dict(plan))}"
        self.socket.send(action_msg)
        result = self._wait_for_msg_type("feedback")
        while not result:
            self.socket.send(f"No feedback response received within {self.timeout} seconds.")
            self.socket.send(action_msg)
            result = self._wait_for_msg_type("feedback", self.timeout)
        feedbacks = [Feedback(False, result.get("logs", "")), Feedback(True, result.get("errors", ""))]
        return feedbacks

    def run_and_feedback(
            self,
            code: str,
            programs: str,
            timeout: float = None,
            executor: Executor = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Runs the provided code with programs as the helper functions in the game environment and returns the observation and info.
        :param code: The code to be executed.
        :param programs: The helper functions to be used by the code.
        :param timeout: The maximum time to allow for code execution. If exceeded, the environment will be reset.
        :param executor: The executor function to run the code. Have to be provided for non-Minecraft game subjects.
        :return: [observation, info] where observation is the game state after code execution and info contains [is_timeout, log_msg, error_msg].
        """

        if self.game_subject in ["DA", "SPD"]:
            raise ValueError("This method is not supported for the current game subject.")

        if timeout is None:
            timeout = self.code_timeout

        if self.game_subject == "MC":
            # Step the environment with the code and programs
            obs, _, _, _, info = self.mine_env.step(code=code, programs=programs, timeout=timeout)

            # If timeout occurs, restart the environment with the last known state
            if info["is_timeout"]:
                self.mine_env.reset(
                    options={
                        "mode": "hard",
                        "username": self.report_prefix,
                        "inventory": obs.get("inventory", {}).get("items", {}),
                        "equipment": obs.get("inventory", {}).get("equipment", [None] * 6),
                        "position": obs.get("status", {}).get("position")
                    }
                )
            return obs, info

        if executor is None:
            raise ValueError("Executor function must be provided for non-Minecraft game subjects when using Plan-to-Code Translator.")

        return executor(code, programs, timeout)