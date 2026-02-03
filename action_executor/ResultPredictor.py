from action_executor.ResultPrediction import ResultPrediction
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from utils.InputGenerator import generate_result_predictor_input
from utils.file_utils import read_file


class ResultPredictor(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_path: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> prediction_reason, quantity, items",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3
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
            num_retries=num_retries
        )

        self.bot_msg = f"{self.game_subject}:action_executor.ResultPredictor:log:"
        self.err_msg = f"{self.game_subject}:action_executor.ResultPredictor:err:"

    def predict(
            self,
            plan: Plan,
            verbose: bool = False,
    ) -> ResultPrediction | None:

        # Load main prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/result_predictor_prompt.txt"
        context = read_file(prompt_path)

        # Convert the current game state to prompt input
        curr_status = generate_result_predictor_input(plan)

        self.c("Query:\n", curr_status)

        # Call the language model
        result_prediction = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful assistant that predicts the result of a plan.",
            context=context,
            question=curr_status
        )

        if not result_prediction:
            self.e("LLM response was empty. Ignore.")
            return None

        self.h("Response:\n", result_prediction)

        prediction_obj = ResultPrediction(
            prediction_reason=result_prediction.reasoning,
            quantity=result_prediction.quantity,
            predicted_items=result_prediction.predicted_items,
        )

        return prediction_obj

