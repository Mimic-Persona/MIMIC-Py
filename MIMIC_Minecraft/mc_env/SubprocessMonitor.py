import time
import re
import warnings
from typing import List

import psutil
import subprocess
import logging
import threading

from ..mc_utils import file_utils as U


class SubprocessMonitor:
    def __init__(
        self,
        commands: List[str],
        name: str,
        ready_match: str = r".*",
        log_path: str = "logs",
        callback_match: str = r"^(?!x)x$",  # regex that will never match
        callback: callable = None,
        finished_callback: callable = None,
    ):
        """
        A class to monitor a subprocess, log its output, and handle readiness and callbacks.
        :param commands: List of commands to start the subprocess.
        :param name: Name of the subprocess for logging purposes.
        :param ready_match: The regex pattern to match when the subprocess is ready.
        :param log_path: Path to the directory where logs will be saved.
        :param callback_match: Regex pattern to match for triggering a callback.
        :param callback: Callable function to be called when the callback_match is found in the output.
        :param finished_callback: Callable function to be called when the subprocess finishes or is stopped.
        """
        self.commands = commands
        self.name = name

        start_time = time.strftime("%Y%m%d_%H%M%S")
        self.logger = logging.getLogger(name)
        handler = logging.FileHandler(U.f_join(log_path, f"{start_time}.log"))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        self.process = None
        self.ready_match = ready_match
        self.ready_event = None
        self.ready_line = None
        self.callback_match = callback_match
        self.callback = callback
        self.finished_callback = finished_callback
        self.thread = None

    def _start(
            self,
    ) -> None:
        """
        Start the subprocess and monitor its output.
        :return: None
        """
        self.logger.info(f"Starting subprocess with commands: {self.commands}")

        # Check if the process is already running and terminate it if so
        if self.process is not None:
            self.process.terminate()
            self.process.wait()

        # Start the subprocess
        self.process = psutil.Popen(
            self.commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        print(f"Subprocess {self.name} started with PID {self.process.pid}.")

        # Read lines from the subprocess output
        for line in iter(self.process.stdout.readline, ""):
            self.logger.info(line.strip())

            # Check if the line matches the ready pattern
            if re.search(self.ready_match, line):
                self.ready_line = line
                self.logger.info("Subprocess is ready.")
                self.ready_event.set()

            # Check if the line matches the callback pattern
            if re.search(self.callback_match, line):
                self.callback()

        if not self.ready_event.is_set():
            # If the ready_event is not set, it means the subprocess did not start correctly
            self.ready_event.set()
            warnings.warn(f"Subprocess {self.name} failed to start.")

        # If the finished_callback is provided, call it
        if self.finished_callback:
            self.finished_callback()

    def run(
            self,
    ) -> None:
        """
        Start the subprocess in a separate thread and wait for it to be ready.
        :return: None
        """
        self.ready_event = threading.Event()
        self.ready_line = None
        self.thread = threading.Thread(target=self._start)
        self.thread.start()
        # block until read_event is set
        print('wait ready_event to set')
        # is it possible that the ready_event is never set?
        # self.ready_event.wait(timeout=60)
        self.ready_event.wait()

    def stop(
            self
    ) -> None:
        """
        Stop the subprocess if it is running.
        :return: None
        """
        self.logger.info("Stopping subprocess.")

        # Check if the process is running before attempting to terminate it
        if self.process and self.process.is_running():
            self.process.terminate()
            self.process.wait()
            self.process = None

    # def __del__(self):
    #     if self.process.is_running():
    #         self.stop()

    @property
    def is_running(
            self,
    ) -> bool:
        """
        Check if the subprocess is currently running.
        :return: True if the subprocess is running, False otherwise.
        """
        if self.process is None:
            return False

        # TODO: 
        # if self.process.is_running() and self.ready_line is None:
        #     self.stop()
        #     raise RuntimeError('Subprocess is running but ready_line is None. It may mean that the process has not started yet.')

        return self.process.is_running()
