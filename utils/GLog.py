import os

from datetime import datetime
from dotenv import load_dotenv

from utils.file_utils import append_file, write_file
from utils.utils import system_say

load_dotenv()

GAME_SUBJECT = os.getenv("GAME_SUBJECT", "default")
AGENT_NAME = os.getenv("AGENT_NAME", "default")
MODEL_NAME = os.getenv("INSTRUCTION_MODEL_NAME", "openai/gpt-4o")
GLOG_EXTRA_DIR = os.getenv("GLOG_EXTRA_DIR", "")
MC_TASK_NAME = os.getenv("MC_TASK", "harvest_1_diamond").lower()
MC_TASK_ID = int(os.getenv("MC_TASK_ID", 0))

# Color constants for terminal output
RESET = "\033[0m"
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
WHITE = "\033[0;37m"


class GLog:
    HIGHLIGHT = "@@ "
    CONNECTION = "$$ "
    AGENT_ERROR = "!! "
    AGENT_COV = "## "
    NEW_LINE = "\n"

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if GAME_SUBJECT == "MC":
        OUT_PATH = f"./out/{GAME_SUBJECT}/{GLOG_EXTRA_DIR}/{MODEL_NAME}/{MC_TASK_NAME}_{MC_TASK_ID}/out_{now_str}_{AGENT_NAME}.log"
    else:
        OUT_PATH = f"./out/{GAME_SUBJECT}/{GLOG_EXTRA_DIR}/{MODEL_NAME}/out_{now_str}_{AGENT_NAME}.log"

    write_file(OUT_PATH, "")
    # write_file(COV_PATH, "")

    is_first_log = True
    BOT_MSG = ""
    ERR_MSG = ""

    @staticmethod
    def i(
            *args
    ):
        """
        Logs a message to the console and appends it to the output file.
        :param args: Message to log, which can include special prefixes for different types of messages, joined by spaces.
        :return: None
        """

        text = " ".join(str(arg) for arg in args).strip()

        if text.startswith(GLog.AGENT_ERROR):
            print(RED + text + RESET)
            GLog.ERR_MSG += text[len(GLog.AGENT_ERROR):] + GLog.NEW_LINE

        elif not text.startswith(GLog.CONNECTION) and not text.startswith(GLog.AGENT_COV):
            print(CYAN + text + RESET)
            GLog.BOT_MSG += text[len(GLog.HIGHLIGHT):] + GLog.NEW_LINE

        elif not text.startswith(GLog.AGENT_COV):
            print(PURPLE + text + RESET)

        if GLog.is_first_log:
            header = f"{'=' * 50} {datetime.now()} {'=' * 50}\n"
            append_file(GLog.OUT_PATH, header)
            # append_text(GLog.COV_PATH, header)
            GLog.is_first_log = False

        if text.startswith(GLog.AGENT_COV):
            print(YELLOW + text + RESET)
            # append_text(GLog.COV_PATH, f"{datetime.now()}\t{text}")
        else:
            append_file(GLog.OUT_PATH, f"{datetime.now()}\t{text}")

    @staticmethod
    def h(text: str, *args):
        GLog.i(GLog.HIGHLIGHT + text, *args)

    @staticmethod
    def c(text: str, *args):
        GLog.i(GLog.CONNECTION + text, *args)

    @staticmethod
    def e(text: str, *args):
        system_say("Error Encountered!")
        GLog.i(GLog.AGENT_ERROR + text, *args)

    @staticmethod
    def cov(text: str, *args):
        GLog.i(GLog.AGENT_COV + text, *args)

    @staticmethod
    def reset_bot_msg():
        GLog.BOT_MSG = ""

    @staticmethod
    def reset_err_msg():
        GLog.ERR_MSG = ""
