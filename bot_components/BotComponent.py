import os

from dotenv import load_dotenv

from llm.LlmModel import LlmModel
from llm.custom_dspy_models.HuggingFaceLlmModel import HuggingFaceLlmModel
from llm.custom_dspy_models.MineMaModel import MineMaModel
from utils.GLog import GLog


def _transfer_task_name(
        task_name: str
) -> str:
    if task_name == "harvest_1_diamond":
        return "Mine 1 Diamond"

    elif task_name == "shear_1_sheep":
        return "Shear 1 Sheep"

    elif task_name == "cook_1_meat":
        return "Cook 1 Meat"

    else:
        return task_name.capitalize().replace("_", " ")


class BotComponent:
    """
    Base class for all bot components.
    """

    def __init__(
            self,
            prompt_root_path: str,
            has_llm: bool = False,
            is_code_module: bool = False,
            instruction_model_name: str = "",
            instruction_model_url: str = "",
            instruction_model_path: str = "",
            instruction_model_provider: str = "",
            code_model_name: str = "",
            code_model_url: str = "",
            code_model_path: str = "",
            code_model_provider: str = "",
            signature: str = "system, context, question -> response",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3,
            loaded_model: type = None,
    ):
        load_dotenv()
        self.game_subject = os.getenv("GAME_SUBJECT", "SPD")
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self.personality = os.getenv("PERSONALITY", "aggression")
        self.report_prefix = os.getenv("AGENT_NAME", "")
        self.is_inherited = os.getenv("IS_CONTINUED", "False").lower() == "true"
        self.base_toggle_threshold = float(os.getenv("BASE_TOGGLE_THRESHOLD", 100))
        self.diverse_toggle_threshold = float(os.getenv("DIVERSE_TOGGLE_THRESHOLD", 20))
        self.task_title = os.getenv("MC_TASK", "harvest_1_diamond").lower()
        self.task_id = int(os.getenv("MC_TASK_ID", 0))
        self.task_name = _transfer_task_name(self.task_title)

        # Determine code language and file extension
        self.code_language = os.getenv("CODE_LANGUAGE", "javascript").lower()
        if self.code_language == "js" or self.code_language == "javascript":
            self.code_language = "javascript"
            self.language_file_extension = ".js"
        else:
            raise ValueError(f"Unsupported code language: {self.code_language}. Supported language is 'javascript'.")

        self.num_code_reties = int(os.getenv("NUM_CODE_RETRIES", 3))

        self.prompt_root_path = prompt_root_path
        self.has_llm = has_llm
        self.is_code_module = is_code_module
        self.instruction_model_name = instruction_model_name
        self.instruction_model_url = instruction_model_url
        self.instruction_model_path = instruction_model_path
        self.instruction_model_provider = instruction_model_provider
        self.code_model_name = code_model_name
        self.code_model_url = code_model_url
        self.code_model_path = code_model_path
        self.code_model_provider = code_model_provider
        self.signature = signature
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_retries = num_retries
        self.is_custom_model = True

        # print(f"Model Path (absolute): {os.path.abspath(self.instruction_model_path)}")
        if self.instruction_model_name.startswith("ollama_chat") or self.instruction_model_name.startswith("openai") or \
            self.code_model_name.startswith("ollama_chat") or self.code_model_name.startswith("openai"):
            self.is_custom_model = False

        # print(f"Loading custom model: {self.is_custom_model}")

        if self.instruction_model_name.startswith("MineMA"):
            if self.game_subject != "MC":
                raise ValueError(f"Invalid model {self.instruction_model_name} for game subject {self.game_subject}. "
                                 f"Only 'MC' supports MineMA models.")

        self.bot_msg = f"{self.game_subject}:bot_components.BotComponent:log:"
        self.err_msg = f"{self.game_subject}:bot_components.BotComponent:err:"

        if self.game_subject == "MC":
            self.is_plan_to_code = True
        elif self.game_subject in ["DA", "SPD"]:
            self.is_plan_to_code = False
        else:
            self.is_plan_to_code = os.getenv("IS_PLAN_TO_CODE", "False").lower() == "true"
            self.h("Unknown game subject, taking value from IS_PLAN_TO_CODE from the .emv file.")

        if self.game_subject == "DA":
            self.plan_signature = "system, context, question -> plan, action, tile, object"

        elif self.game_subject == "SPD":
            self.plan_signature = "system, context, question -> plan, action, tile, item1, item2, wait_turns"

        else:
            self.plan_signature = "system, context, question -> plan, action, object"

        self.decomposer_signature = "system, context, question -> plans"

        self.decision_signature = "system, context, question -> plan, decision, reason, critique"

        self.result_prediction_signature = "system, context, question -> quantity: int, predicted_items: list[str]"

        self.code_signature = "system, context, question -> code_design, skill_name, used_skills_name, code, code_failing_reason"

        self.time_prediction_signature = "system, context, question -> time_prediction: float"

        self.summary_signature = "system, context, question -> summary, is_success: bool, critique"

        self.skill_description_signature = "system, context, question -> description"

        self.preference_analysis_signature = "system, context, question -> analysis"

        if loaded_model:
            self.llm = loaded_model

        elif self.has_llm and self.instruction_model_name.startswith("MineMA") and not self.is_code_module:
            self.llm = MineMaModel(
                model_name=self.instruction_model_name,
                model_path=self.instruction_model_path,
                signature=self.signature,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                num_retries=self.num_retries
            )

        elif self.has_llm and self.instruction_model_name.startswith("MineMA") and self.is_code_module:
            self.llm = MineMaModel(
                model_name=self.code_model_name,
                model_path=self.code_model_path,
                signature=self.signature,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                num_retries=self.num_retries
            )

        elif self.has_llm and self.is_custom_model and not self.is_code_module:
            self.llm = HuggingFaceLlmModel(
                model_name=self.instruction_model_name,
                model_path=self.instruction_model_path,
                signature=self.signature,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                num_retries=self.num_retries
            )

        elif self.has_llm and self.is_custom_model and self.is_code_module:
            self.llm = HuggingFaceLlmModel(
                model_name=self.code_model_name,
                model_path=self.code_model_path,
                signature=self.signature,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                num_retries=self.num_retries
            )

        elif self.has_llm and not self.is_code_module:
            self.llm = LlmModel(model_name=self.instruction_model_name,
                                model_url=self.instruction_model_url,
                                model_provider=self.instruction_model_provider,
                                api_key=self._api_key,
                                signature=self.signature,
                                temperature=self.temperature,
                                max_tokens=self.max_tokens,
                                num_retries=self.num_retries)

        elif self.has_llm and self.is_code_module:
            self.llm = LlmModel(model_name=self.code_model_name,
                                model_url=self.code_model_url,
                                model_provider=self.code_model_provider,
                                api_key=self._api_key,
                                signature=self.signature,
                                temperature=self.temperature,
                                max_tokens=self.max_tokens,
                                num_retries=self.num_retries)

        else:
            self.llm = None

    def c(self, text: str, *args):
        """
        Logs a normal connection message.
        """
        GLog.c(self.bot_msg, text, *args)

    def h(self, text: str, *args):
        """
        Logs a highlighted message.
        """
        GLog.h(self.bot_msg, text, *args)

    def e(self, text: str, *args):
        """
        Logs an error message.
        """
        GLog.e(self.err_msg, text, *args)
