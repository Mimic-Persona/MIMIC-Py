from bot_components.BotComponent import BotComponent
from hybrid_planner.Decision import Decision
from hybrid_planner.Plan import Plan


class PlanDecider(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_path: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> Decision",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3,
            loaded_model: type = None,
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=False,
            is_code_module=False,
            instruction_model_name=model_name,
            instruction_model_url=model_url,
            instruction_model_path=model_path,
            instruction_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries,
            loaded_model=loaded_model
        )
        self.bot_msg = f"{self.game_subject}:hybrid_planner.PlanDecider:log:"
        self.err_msg = f"{self.game_subject}:hybrid_planner.PlanDecider:err:"

    def _SPD_decide(
            self,
            plan: Plan
    ) -> Decision:
        """
        SPD specific rule for deciding the plan.
        """
        pass

    def decide(
            self,
            latest_bad_plans: list[Decision],
            plan: Plan
    ) -> Decision:
        """
        Decides whether a given plan is acceptable based on predefined rules.
        :param latest_bad_plans: List of previously rejected plans.
        :param plan: The plan to be evaluated.
        :return: Decision object containing the decision, reason, and critique.
        """
        if not plan:
            decision = Decision(
                plan=plan.plan,
                decision=False,
                reason="The plan is empty.",
                critique="Try to remake a plan first."
            )
            self.c(str(decision))
            return decision

        # 0. Check if the plan is provided
        if plan.plan is None or plan.plan.strip() == "...":
            decision = Decision(
                plan=plan.plan,
                decision=False,
                reason="The plan is empty.",
                critique="Try to remake a plan first. Make sure the plan is not just '...' but following the format of the plan signature and is a valid plan."
            )
            self.c(str(decision))
            return decision

        # 1. Check if any 'item' keyword contains multiple objects
        for key, value in vars(plan).items():
            if "item" in key and any(sep in value for sep in [" and ", ",", " or ", "&"]):
                decision = Decision(
                    plan=plan.plan,
                    decision=False,
                    reason="The object is more than one.",
                    critique="Try to make the object be only one type or try another task."
                )
                self.c(str(decision))
                return decision

        # 2. Check if the plan has been previously rejected
        count = sum(1 for bad in latest_bad_plans if bad.plan.lower() == plan.plan.lower())

        if count >= 3:
            decision = Decision(
                plan=plan.plan,
                decision=True,
                reason="The task appears more than 3 times in 1 cycle. Give it a try!",
                critique=""
            )
        elif count > 0:
            decision = Decision(
                plan=plan.plan,
                decision=False,
                reason="The plan is already rejected.",
                critique="Try to make the plan better or try another task."
            )
        else:
            decision = Decision(
                plan=plan.plan,
                decision=True,
                reason="The plan is acceptable.",
                critique=""
            )

        self.h(f'Decision for Plan "{plan.plan}":\n', str(decision.to_dict()))
        return decision
