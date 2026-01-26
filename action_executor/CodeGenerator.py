from action_executor.Code import Code
from action_executor.Execution import Execution
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from skill_system.SkillSystem import SkillSystem
from summarizer.Summary import Summary
from utils.InputGenerator import generate_code_generator_input
from utils.dspy_utils import parse_code_str
from utils.file_utils import read_file


class CodeGenerator(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            skill_system: SkillSystem,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> code_design, skill_name, used_skills_name, code, code_failing_reason",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=True,
            is_code_module=True,
            code_model_name=model_name,
            code_model_url=model_url,
            code_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.skill_system = skill_system

        self.bot_msg = f"{self.game_subject}:action_executor.CodeGenerator:log:"
        self.err_msg = f"{self.game_subject}:action_executor.CodeGenerator:err:"

    def generate(
            self,
            status: dict,
            plan: Plan,
            prev_code: Code = None,
            prev_execution: Execution = None,
            prev_summary: Summary = None,
            verbose: bool = False,
    ) -> Code | None:
        """
        Generates code based on the current game state, plan, and previous execution results.
        :param status: The Current game states as a dictionary.
        :param plan: The plan that was executed or is to be executed.
        :param prev_code: The code generated in the previous step, if any.
        :param prev_execution: Execution results from the previous step, if any.
        :param prev_summary: Summary of the previous execution, if available.
        :return: Code object containing the generated code and related attributes, or None if generation fails.
        """
        # Load main prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/code_generator_prompt.txt"
        context = read_file(prompt_path)

        # Load skills
        basic_skills_context = self.skill_system.basic_skills
        related_skills = self.skill_system.retrieve_by_relevance(plan)
        related_skills_context = self.skill_system.skills_code_to_str(related_skills)

        # Replace placeholders
        context = context.replace("{Basic_Skills}", basic_skills_context)
        context = context.replace("{Skills}", related_skills_context)

        # Convert the current game state to prompt input
        curr_status = generate_code_generator_input(
            game_subject=self.game_subject,
            status=status,
            plan=plan,
            prev_code=prev_code,
            prev_execution=prev_execution,
            prev_summary=prev_summary,
        )

        self.h("Basic Skills:\n", basic_skills_context)
        self.h("Related Skills:\n", related_skills_context)

        self.c("Query:\n", curr_status)

        # Call the language model
        code = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful assistant for coding.",
            context=context,
            question=curr_status
        )

        if not code:
            self.e("LLM response was empty. Ignore.")
            return None

        self.h("Response:\n", code)

        # Get all the attr of time_prediction
        try:
            attrs = parse_code_str(str(code))
            attrs.pop('reasoning', None)
            code_obj = Code(**attrs)  # if you have a dataclass or object

        except Exception as e:
            self.e("Failed to parse code string: %s", str(e))
            return None

        return code_obj
