import os.path
import time
import warnings
from typing import SupportsFloat, Any, Tuple, Dict

import requests
import json

import gymnasium as gym
from gymnasium.core import ObsType
from dotenv import load_dotenv

from ..mc_utils import file_utils as U

from ..mc_utils.logger import get_logger, Timer
from ..mc_utils.run_utils import retry
from .MineInstance import MineInstance
from .SubprocessMonitor import SubprocessMonitor


class MineEnv(gym.Env):
    def __init__(
            self,
            request_timeout: int = 600000,
            log_path: str = "./logs",
            is_planner_only: bool = False,
    ):
        """
        Initialize the MineEnv environment.
        :param request_timeout: The timeout for requests to the server in milliseconds. Default is 600000 (10 minutes).
        :param log_path: The path where logs will be stored. Default is "./logs".
        :param is_planner_only: If True, the environment will be set up for planner-only actions. Default is False.
        :raises ValueError: If neither mc_port nor azure_login is specified.
        """
        load_dotenv()

        self.mc_host = os.getenv("MC_HOST", "localhost")
        self.mc_port = int(os.getenv("MC_PORT", None))
        self.azure_login = json.loads(os.getenv("AZURE_LOGIN") or "{}")
        self.is_planner_only = is_planner_only

        if not self.mc_port and not self.azure_login:
            raise ValueError("Either mc_port or azure_login must be specified")

        if self.mc_port and self.azure_login:
            warnings.warn("Both mc_port and azure_login are specified, mc_port will be ignored")

        self.logger = get_logger('MineEnv')

        self.server_host = os.getenv("SERVER_HOST", "http://127.0.0.1")
        self.server_port = int(os.getenv("SERVER_PORT", 3000))
        self.server = f"{self.server_host}:{self.server_port}"

        self.socket_host = os.getenv("SOCKET_HOST", "127.0.0.1")
        self.socket_port = int(os.getenv("SOCKET_PORT", 1111))

        self.request_timeout = request_timeout
        self.log_path = log_path
        self.mineflayer = self.get_mineflayer_process(self.server_port)

        self.task = os.getenv("TASK", "example")
        self.id = int(os.getenv("ID", 0))

        if self.azure_login:
            self.mc_instance = self.get_mc_instance()
        else:
            self.mc_instance = None

        self.has_reset = False
        self.reset_options = None
        self.connected = False
        self.server_paused = False

    def get_mineflayer_process(
            self,
            server_port: int
    ) -> SubprocessMonitor:
        """
        Get the Mineflayer process.
        :param server_port: The port on which the Mineflayer server will run.
        :return: SubprocessMonitor instance for Mineflayer.
        """
        U.f_mkdir(self.log_path, "mineflayer")
        file_path = os.path.abspath(os.path.dirname(__file__))

        return SubprocessMonitor(
            commands=[
                "node",
                U.f_join(file_path, "mineflayer/index.js"),
                str(server_port),
            ],
            name="mineflayer",
            ready_match=r"Server started on port (\d+)",
            log_path=U.f_join(self.log_path, "mineflayer"),
        )

    def get_mc_instance(
            self
    ) -> MineInstance:
        """
        Get the Minecraft instance.
        :return: MineInstance instance.
        """
        self.logger.info('create minecraft server')
        U.f_mkdir(self.log_path, "minecraft")

        return MineInstance(
            **self.azure_login,
            mineflayer=self.mineflayer,
            log_path=U.f_join(self.log_path, "minecraft"),
        )

    def check_process(
            self
    ) -> Any | None:
        """
        Make sure the Minecraft server and Mineflayer process are running.
        If the Minecraft server is not running, it will start the server.
        If the Mineflayer process is not running, it will start the process and then send a request to the server to start the Minecraft server.
        If both processes are running, it will return None.
        :return: None if both processes are running, otherwise returns the response from the server.
        """
        if self.mc_instance and not self.mc_instance.is_running:
            # if self.mc_instance:
            #     self.mc_instance.check_process()
            #     if not self.mc_instance.is_running:
            self.logger.info('Start Minecraft server')
            self.mc_instance.run()
            self.mc_port = self.mc_instance.port
            self.reset_options["mc_port"] = self.mc_instance.port
            self.logger.info(f"Server started on port {self.reset_options['mc_port']}")

        if not self.mineflayer.is_running:
            # Mineflayer process is not running, start it
            retry = 3
            while retry > 0:
                self.logger.info('Start Mineflayer process')
                with Timer('check process run mineflayer'):
                    self.mineflayer.run()

                # Wait for Mineflayer to be ready
                if not self.mineflayer.is_running:
                    # Mineflayer process failed to start
                    if retry == 0:
                        raise RuntimeError("Mineflayer process failed to start")
                    else:
                        self.logger.warning('Try to restart mineflayer again, after sleep 1 second')
                        time.sleep(1)

                    retry -= 1

                else:
                    # Mineflayer process started successfully
                    self.logger.info(f'mineflayer ready line: {self.mineflayer.ready_line}')
                    if self.mineflayer.ready_line is None:
                        self.logger.critical('mineflayer read line is None.')
                    break

            # Send a request to the server to start the Minecraft server
            retry = 3
            while retry > 0:
                try:
                    # Send a request to the server to start the Minecraft server
                    res = requests.post(
                        f"{self.server}/start",
                        json=self.reset_options,
                        timeout=self.request_timeout,
                    )

                    # Check the response status code
                    if res.status_code == 200:
                        # The server started successfully
                        self.logger.debug(f'start response:{res.json()}')
                        return res.json()

                    else:
                        # The server failed to start
                        if retry == 0:
                            self.mineflayer.stop()
                            raise RuntimeError("Reset Minecraft server failed!")
                        else:
                            self.logger.warning(f'Reset Minecraft server {res.status_code}')
                            time.sleep(3)

                        retry -= 1

                except requests.exceptions.Timeout:
                    # The request to start the server timed out
                    if retry == 0:
                        self.mineflayer.stop()
                        raise RuntimeError("Reset Minecraft server timeout!")

                    else:
                        self.logger.warning(f"Reset Minecraft server timeout, retrying")
                        time.sleep(1)

                    retry -= 1

        else:
            self.logger.info('Mineflayer process is running')
            return None

    def step(
            self,
            code: str = "",
            programs: str = "",
            timeout: float = 600000.0,
            retry: int = 3,
    ) -> Tuple[dict[str, Any], SupportsFloat, bool, bool, Dict[str, Any]]:
        """
        Step the Minecraft environment with the given code and programs.
        :param code: The code to execute in the Minecraft environment.
        :param programs: The programs to run in the Minecraft environment.
        :param timeout: The timeout for the step in milliseconds. Default is 600000 (10 minutes).
        :param retry: The number of times to retry the step if it fails. Default is 3.
        :return: Tuple containing the observation, reward, done flag, truncated flag, and additional info.
        """
        if not self.has_reset:
            raise RuntimeError("Environment has not been reset yet")

        # Make sure the Minecraft server and Mineflayer process are running
        self.check_process()
        self.unpause()

        data = {
            "code": code,
            "programs": programs,
            "timeout": timeout,
        }

        while retry > 0:
            try:
                with Timer('post step'):
                    res = requests.post(
                        f"{self.server}/step", json=data, timeout=self.request_timeout
                    )

                    if res.status_code == 200:
                        self.logger.debug(f'response:{res.json()}')
                        break

                    else:
                        retry -= 1
                        self.logger.warning(f"Step Minecraft server failed, retrying")
                        if retry == 0:
                            raise RuntimeError("Step Minecraft server failed!")

            except requests.exceptions.Timeout:
                retry -= 1
                self.logger.warning(f"Step Minecraft server timeout, retrying")

                if retry == 0:
                    raise RuntimeError("Step Minecraft server timeout!")

                res = requests.post(
                    f"{self.server}/start",
                    json=self.reset_options,
                    timeout=self.request_timeout,
                )

        # if res.status_code != 200:
        #     raise RuntimeError("Failed to step Minecraft server")

        returned_data = res.json()
        self.pause()
        obs = returned_data.get("observation", "")

        if not obs:
            raise RuntimeError("Observation from Minecraft server is empty or invalid")

        # Extract the observation from the returned data
        if obs.find('[["observe",') != -1:
            obs = obs[obs.find('[["observe",') + 12 : -2]

        elif obs.find(',["observe",') != -1:
            obs = obs[obs.find(',["observe",') + 12 : -2]

        obs = json.loads(obs)

        bot_msg = returned_data.get("botMsg", "")
        err_msg = returned_data.get("errMsg", "")
        is_timeout = returned_data.get("isTimeout", False)

        reward = 0.0
        terminated = False
        truncated = False
        info = {
            "is_timeout": is_timeout,
            "bot_msg": bot_msg,
            "err_msg": err_msg,
        }

        return obs, reward, terminated, truncated, info

    def observe(
            self,
            retry: int = 3,
    ) -> dict[str, Any]:
        """
        Observe the Minecraft environment.
        :param retry: The number of times to retry the observation if it fails. Default is 3.
        :return: The observation from the Minecraft environment.
        """
        if not self.has_reset:
            raise RuntimeError("Environment has not been reset yet")

        self.check_process()

        while retry > 0:
            try:
                with Timer('post observe'):
                    res = requests.post(
                        f"{self.server}/observe",
                        timeout=self.request_timeout,
                    )

                if res.status_code != 200:
                    raise RuntimeError(f"Failed to observe Minecraft server: {res.text}")

            except requests.exceptions.Timeout:
                retry -= 1
                self.logger.warning(f"Observe Minecraft server timeout, retrying")

                if retry == 0:
                    raise RuntimeError("Observe Minecraft server timeout!")

                self.unpause()

                res = requests.post(
                    f"{self.server}/start",
                    json=self.reset_options,
                    timeout=self.request_timeout,
                )

            returned_data = res.json()
            obs = returned_data.get("observation", "")

            if not obs:
                raise RuntimeError("Observation from Minecraft server is empty or invalid")

            obs = obs[obs.find('[["observe",') + 12 : -2]
            obs = json.loads(obs)

            return obs

    def render(
            self,
    ) -> None:
        """
        Render the Minecraft environment.
        This method is not implemented in this base class and should be overridden in subclasses.
        :return: None
        """
        raise NotImplementedError("render is not implemented")

    def reset(
            self,
            *,
            seed=None,
            options=None,
    ) -> Tuple[ObsType, Dict[str, Any]]:
        """
        Reset the Minecraft environment.
        :param seed: The seed for the reset. Not used in this implementation.
        :param options: A dictionary of options for the reset. It can include:
            - "mode": The reset mode, either "hard" or "soft". Default is "hard".
            - "inventory": A dictionary representing the inventory to set. Only valid in "hard" mode.
            - "equipment": A list of equipment to set.
            - "spread": Whether to spread the player across the world. Default is False.
            - "wait_ticks": The number of ticks to wait after resetting. Default is 5.
            - "position": The position to reset the player to. Default is None.
            - "username": The username for the player. Default is 'bot'.
        :return: A tuple containing the initial observation and additional info.
        """
        self.unpause()
        self.logger.info('reset node server')
        if options is None:
            options = {}

        if options.get("inventory", {}) and options.get("mode", "hard") != "hard":
            raise RuntimeError("inventory can only be set when options is hard")

        self.reset_options = {
            "mc_host": self.mc_host,
            "mc_port": self.mc_port,
            "socket_host": self.socket_host,
            "socket_port": self.socket_port,
            "task": self.task,
            "id": self.id,
            "is_player_observer": self.is_planner_only,
            "reset": options.get("mode", "hard"),
            "inventory": options.get("inventory", {}),
            "equipment": options.get("equipment", []),
            "spread": options.get("spread", False),
            "waitTicks": options.get("wait_ticks", 5),
            "position": options.get("position", None),
            "username": options.get('username', 'bot'),
        }

        with Timer('reset unpause mc server'):
            self.unpause()

        with Timer('reset stop mc_server'):
            self.mineflayer.stop()
        time.sleep(1)  # wait for mineflayer to exit

        with Timer('reset check_process'):
            returned_data = self.check_process()

        self.has_reset = True
        self.connected = True

        # All the reset in step will be soft
        self.reset_options["reset"] = "soft"
        self.pause()

        if returned_data is None:
            self.logger.warning('reset return None')
            return None
        return json.loads(returned_data)

    def close(
            self,
    ) -> bool:
        """
        Close the Minecraft environment.
        :return: True if the environment was successfully closed, False otherwise.
        """
        self.unpause()

        if self.connected:
            res = requests.post(f"{self.server}/stop")

            if res.status_code == 200:
                self.connected = False

        if self.mc_instance:
            self.mc_instance.stop()

        self.mineflayer.stop()

        return not self.connected

    @retry(retry_count=3)
    def pause(self):
        """
        Pause the Minecraft server.
        :return: True if the server was successfully paused, False otherwise.
        """
        if self.mineflayer.is_running and not self.server_paused:
            res = requests.post(f"{self.server}/pause")

            if res.status_code == 200:
                self.server_paused = True

            else:
                self.logger.warning(f"Failed to pause Minecraft server {res.status_code}")
                raise RuntimeError("Failed to pause Minecraft server")

        return self.server_paused

    @retry(retry_count=3)
    def unpause(self):
        """
        Unpause the Minecraft server.
        :return: True if the server was successfully unpaused, False otherwise.
        """
        if self.mineflayer.is_running and self.server_paused:
            res = requests.post(f"{self.server}/pause")

            if res.status_code == 200:
                self.server_paused = False

            else:
                self.logger.warning(f"Failed to unpause Minecraft server {res.status_code}")
                raise RuntimeError("Failed to unpause Minecraft server")

        return self.server_paused
