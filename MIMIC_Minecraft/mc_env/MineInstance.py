import os
import re

import minecraft_launcher_lib
import sys
from ..mc_utils import file_utils as U

from .SubprocessMonitor import SubprocessMonitor


class MineInstance:
    def __init__(
        self,
        client_id: str,
        redirect_url: str,
        secret_value: str,
        mineflayer: SubprocessMonitor,
        version: str = "1.19",
        log_path: str = "./logs",
    ):
        self.client_id = client_id
        self.redirect_url = redirect_url
        self.secret_value = secret_value
        self.version = version
        self.log_path = log_path
        self.mc_dir = minecraft_launcher_lib.utils.get_minecraft_directory()
        self.port = None

        def stop_mineflayer():
            """
            Stop the mineflayer process if it is running.
            :return: None
            """
            print("Stopping mineflayer")

            try:
                mineflayer.stop()

            except Exception as e:
                print(e)


        self.mc_command = self.get_mc_command()

        # Create the mineflayer process
        self.mc_process = SubprocessMonitor(
            commands=self.mc_command,
            name="minecraft",
            ready_match=r"Started serving on (\d+)",
            log_path=self.log_path,
            callback=stop_mineflayer,
            callback_match=r"\[Server thread/INFO\]: bot left the game",
            finished_callback=stop_mineflayer,
        )

    def get_mineflayer_process(
            self,
            server_port: int,
    ) -> SubprocessMonitor:
        """
        Create a mineflayer process to interact with the Minecraft server.
        :param server_port: The port on which the Minecraft server is running.
        :return: SubprocessMonitor instance for the mineflayer process.
        """
        U.f_mkdir(self.log_path, "../mineflayer")
        file_path = os.path.abspath(os.path.dirname(__file__))

        # Create the mineflayer process
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

    def get_mc_command(
            self
    ) -> list:
        """
        Get the Minecraft command to run the server.
        :return: list: The command to run the Minecraft server.
        """
        file_path = os.path.abspath(os.path.dirname(__file__))

        # Check if the config file exists, if not, perform the login process
        if not U.f_exists(file_path, "config.json"):
            (
                login_url,
                state,
                code_verifier,
            ) = minecraft_launcher_lib.microsoft_account.get_secure_login_data(
                self.client_id, self.redirect_url
            )
            print(
                f"Please open {login_url} in your browser and copy the url you are redirected into the prompt below."
            )
            code_url = input()

            try:
                auth_code = (
                    minecraft_launcher_lib.microsoft_account.parse_auth_code_url(
                        code_url, state
                    )
                )

            except AssertionError:
                print("States do not match!")
                sys.exit(1)

            except KeyError:
                print("Url not valid")
                sys.exit(1)

            login_data = minecraft_launcher_lib.microsoft_account.complete_login(
                self.client_id,
                self.secret_value,
                self.redirect_url,
                auth_code,
                code_verifier,
            )

            options = {
                "username": login_data["name"],
                "uuid": login_data["id"],
                "token": login_data["access_token"],
            }
            U.json_dump(options, file_path, "config.json")
            print(f"Login success, save to {U.f_join(file_path, 'config.json')}")

        # Load the options from the config file
        options = U.json_load(file_path, "config.json")

        # Get the Minecraft command to run the server
        mc_command = minecraft_launcher_lib.command.get_minecraft_command(
            self.version, self.mc_dir, options
        )

        return mc_command

    def run(
            self,
    ) -> None:
        """
        Run the Minecraft server process and extract the port from the output.
        :return: None
        """
        self.mc_process.run()
        pattern = r"Started serving on (\d+)"
        match = re.search(pattern, self.mc_process.ready_line)

        # Extract the port from the ready line
        if match:
            self.port = int(match.group(1))
            print("The mc server is listening on port", self.port)

        # If the port is not found, raise an error
        else:
            raise RuntimeError("Port not found")

    def stop(
            self,
    ) -> None:
        """
        Stop the Minecraft server process.
        :return: None
        """
        self.mc_process.stop()

    @property
    def is_running(
            self,
    ) -> bool:
        """
        Check if the Minecraft server process is running.
        :return: True if the process is running, False otherwise.
        """
        return self.mc_process.is_running
