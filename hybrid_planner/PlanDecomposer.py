import json

from typing import Optional
from bot_components.BotComponent import BotComponent
from hybrid_planner.Decision import Decision
from hybrid_planner.Plan import Plan
from utils.InputGenerator import generate_plan_decomposer_input
from utils.file_utils import read_file


class PlanDecomposer(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> plans",
            temperature: float = 0.0,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=True,
            is_code_module=False,
            instruction_model_name=model_name,
            instruction_model_url=model_url,
            instruction_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )
        self.bot_msg = f"{self.game_subject}:hybrid_planner.PlanDecomposer:log:"
        self.err_msg = f"{self.game_subject}:hybrid_planner.PlanDecomposer:err:"

    def decompose(
            self,
            status: dict,
            plan: Plan,
            latest_bad_sub_plans: list[Decision],
            verbose: bool = False,
    ) -> Optional[list[Plan]]:
        """
        Decomposes a high-level plan into sub-plans using an LLM.

        :param status: Current environment/game state.
        :param plan: The top-level plan to decompose.
        :param latest_bad_sub_plans: Recently failed or incorrect sub-plans.
        :return: A list of sub-plans, or None if decomposition fails.
        """
        # Load system context prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/plan_decompose_prompt.txt"
        context = read_file(prompt_path)

        # Construct input to the LLM
        input_str = generate_plan_decomposer_input(
            game_subject=self.game_subject,
            status=status,
            plan=plan,
            latest_bad_sub_plans=latest_bad_sub_plans
        )
        self.c("Query:\n", input_str)

        # Get sub-plans from the LLM
        sub_plans = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful plan decomposer.",
            context=context,
            question=input_str
        ).plans

        if not sub_plans:
            self.c("LLM response was empty. Ignoring.")
            return None

        sub_plans = [Plan.from_dict(p) for p in json.loads(sub_plans)]

        self.c(f'Decomposed Sub-Plans for Plan "{plan.plan}":\n', sub_plans)
        return sub_plans
