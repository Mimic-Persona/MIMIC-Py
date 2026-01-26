import os
import time
from typing import Literal

from bot_components.BotComponent import BotComponent
from hybrid_planner.Decision import Decision
from hybrid_planner.Plan import Plan
from memory_system.MemorySystem import MemorySystem
from utils.InputGenerator import generate_planner_input
from utils.file_utils import read_file


class Planner(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            planner_type: Literal["bottomUp", "topDown"],
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_path: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> Plan",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3,
            is_bottom_up_only: bool = False,
            is_top_down_only: bool = False,
            with_feedback: bool = False,
            loaded_model: type = None,
    ):
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=True,
            is_code_module=False,
            instruction_model_name=model_name,
            instruction_model_url=model_url,
            instruction_model_path=model_path,
            instruction_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries,
            loaded_model=loaded_model,
        )

        if planner_type not in ["bottomUp", "topDown"]:
            raise ValueError(f"Invalid planner type: {planner_type}. Must be 'bottomUp' or 'topDown'.")

        self.planner_type = planner_type

        self.is_bottom_up_only = is_bottom_up_only
        self.is_top_down_only = is_top_down_only
        self.with_feedback = with_feedback

        self.bot_msg = f"{self.game_subject}:hybrid_planner.Planner-{self.planner_type}:log:"
        self.err_msg = f"{self.game_subject}:hybrid_planner.Planner-{self.planner_type}:err:"

    def plan(
            self,
            memory_stream: MemorySystem | None,
            status: dict,
            latest_bad_plans: list[Decision],
            is_retrieve_separate: bool = True,
            recent_plans: list[Plan | dict] | None = None,
            verbose: bool = False,
            noise: bool = False,
    ) -> Plan | None:
        """
        Generates a plan based on the current game state and personality context.
        :param memory_stream: Memory system to retrieve recent memories.
        :param status: The Current game states as a dictionary.
        :param latest_bad_plans: List of the latest rejected plans to inform the planner.
        :param is_retrieve_separate: Indicates if the retrieval method is separate. If separated, use RP, otherwise, use U.
        :param recent_plans: Optional list of recent plans to consider in the planning process. Only used if in planner-only experiment.
        :return: A Plan object containing the generated plan.
        """
        personalities_path = f"{self.prompt_root_path}/{self.game_subject}/personalities"
        persa_context = read_file(f"{personalities_path}/{self.personality}.txt")
        persa_example_context = read_file(f"{personalities_path}/{self.personality}_examples.txt")

        # Load main prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/{self.planner_type}_plan_prompt_RP.txt" if is_retrieve_separate \
            else f"{self.prompt_root_path}/{self.game_subject}/{self.planner_type}_plan_prompt_U.txt"
        context = read_file(prompt_path)

        if self.is_bottom_up_only and not self.with_feedback:
            context = read_file(f"{self.prompt_root_path}/{self.game_subject}/exp/bottomUp_planner_only_prompt.txt")
        elif self.is_top_down_only and not self.with_feedback:
            context = read_file(f"{self.prompt_root_path}/{self.game_subject}/exp/topDown_planner_only_prompt.txt")
        elif self.is_bottom_up_only and self.with_feedback:
            context = read_file(f"{self.prompt_root_path}/{self.game_subject}/exp/bottomUp_planner_only_with_feedback_prompt.txt")
        elif self.is_top_down_only and self.with_feedback:
            context = read_file(f"{self.prompt_root_path}/{self.game_subject}/exp/topDown_planner_only_with_feedback_prompt.txt")

        # Replace placeholders
        context = context.replace("{Personalities}", persa_context)
        context = context.replace("{Personalities_Examples}", persa_example_context)

        if self.game_subject == "MC":
            context = context.replace("{Task_Name}", self.task_name)

            task_prompt_path = f"{self.prompt_root_path}/{self.game_subject}/task_suit/{self.task_title}.txt"
            if not os.path.isfile(task_prompt_path):
                # If the task prompt file does not exist, log a message and continue without it
                self.h(f"Task prompt file {task_prompt_path} does not exist. Continuing without task description.")
                context = context.replace("{Task_Description}", "")
            else:
                # Read the task description from the file
                context = context.replace("{Task_Description}", read_file(task_prompt_path))

        if noise:
            # Add noise to the context for testing purposes
            context = f"{time.time()}\n{context}"

        # Convert the current game state to prompt input
        curr_status = generate_planner_input(
            self.game_subject,
            status,
            memory_stream,
            latest_bad_plans,
            is_planner_only=self.is_bottom_up_only or self.is_top_down_only,
            recent_plans=recent_plans
        )

        self.c("Query:\n", curr_status)

        # Call the language model
        new_plan = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful planner.",
            context=context,
            question=curr_status,
        )

        if not new_plan:
            self.e("LLM response was empty. Ignore.")
            return None

        self.h("Response:\n", new_plan)

        if not self.is_custom_model:
            if hasattr(new_plan, "_store"):
                attrs = new_plan._store
            elif hasattr(new_plan, "dict"):
                attrs = new_plan.dict()
            else:
                self.e("Unsupported prediction structure. Cannot extract plan fields.")
                return None
        else:
            attrs = new_plan

        plan_reason = attrs.pop("reasoning", None)
        plan_obj = Plan(plan_reason=plan_reason, **attrs)

        self.c("New Plan:\n", plan_obj.to_dict())

        return plan_obj