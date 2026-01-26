import re
import time

from action_executor.Code import Code
from action_executor.Execution import Execution
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from summarizer.Summary import Summary
from utils.InputGenerator import generate_summarizer_input
from utils.file_utils import read_file


class Summarizer(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_path: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> Summary",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3,
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

        self.bot_msg = f"{self.game_subject}:summarizer.Summarizer:log:"
        self.err_msg = f"{self.game_subject}:summarizer.Summarizer:err:"

    def summarize(
            self,
            prev_status: dict,
            curr_status: dict,
            plan: Plan,
            execution: Execution,
            code: Code = None,
            is_planner_only: bool = False,
            verbose: bool = False,
            noise: bool = False
    ) -> Summary | None:
        """
        Generates a summary of the current game state, plan, and execution results.
        :param prev_status: The Previous game state as a dictionary.
        :param curr_status: The Current game states as a dictionary.
        :param plan: The plan that was executed.
        :param execution: The execution results of the plan.
        :param code: The code that was executed, if applicable.
        :return: A Summary object containing the generated summary, or None if the summary could not be generated.
        """
        if execution.is_timeout:
            self.h("Execution timed out. Auto-generate summarization:")

            summary_obj = Summary(
                plan=plan,
                summary="The execution did not complete within the allowed time limit. No results available.",
                is_success=False,
                critique="Please check if there is any infinite loop in the code or the feasibility of the code according to current in-game environment.",
            )

            self.c(f'Summary of Plan "{plan.plan}:"\n', summary_obj.to_dict())
            return summary_obj

        # Load summarization prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/event_summarize_prompt.txt"
        if execution.is_error:
            prompt_path = f"{self.prompt_root_path}/{self.game_subject}/error_summarize_prompt.txt"

        if self.game_subject == "MC":
            prompt_path = f"{self.prompt_root_path}/{self.game_subject}/event_summarize_difference_prompt.txt"

        if is_planner_only:
            prompt_path = f"{self.prompt_root_path}/{self.game_subject}/exp/summarizer_prompt.txt"

        context = read_file(prompt_path)

        if noise:
            # Add noise to the context for testing purposes
            context = f"{time.time()}\n{context}"

        # Convert info to prompt input
        input_data = generate_summarizer_input(
            game_subject=self.game_subject,
            prev_status=prev_status,
            curr_status=curr_status,
            plan=plan,
            execution=execution
        )

        self.c("Query:\n", input_data)

        # Call the language model
        summary = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful summarizer.",
            context=context,
            question=input_data,
        )

        if not summary:
            self.e("LLM response was empty. Ignore.")
            return None

        self.h("Response:\n", summary)

        if not self.is_custom_model:
            if hasattr(summary, "_store"):
                attrs = summary._store
            elif hasattr(summary, "dict"):
                attrs = summary.dict()
            else:
                self.e("Unsupported prediction structure. Cannot extract summary fields.")
                return None
        else:
            attrs = summary

        # Get all the attr of summary_obj
        summary_obj = Summary(
            summary=attrs.get("summary", ""),
            is_success=attrs.get("is_success", False),
            critique=attrs.get("critique", ""),
            plan=plan
        )

        self.c(f'Summary of Plan "{plan.plan}:"\n', summary_obj.to_dict())

        return summary_obj
