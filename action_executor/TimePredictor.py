from action_executor.ResultPrediction import ResultPrediction
from action_executor.TimePrediction import TimePrediction
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from utils.InputGenerator import generate_time_predictor_input
from utils.file_utils import read_file


class TimePredictor(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> time_prediction",
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
            instruction_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.bot_msg = f"{self.game_subject}:action_executor.TimePredictor:log:"
        self.err_msg = f"{self.game_subject}:action_executor.TimePredictor:err:"

    def predict(
            self,
            curr_status: dict,
            plan: Plan,
            result_prediction: ResultPrediction,
            code: str,
            verbose: bool = False,
    ) -> TimePrediction | None:
        """
        Predicts the time required to complete a plan based on the current game state, plan details, and code to execute.
        :param curr_status: The Current game states as a dictionary.
        :param plan: The plan to be executed.
        :param result_prediction: ResultPrediction object containing the expected results of the plan.
        :param code: The code that will be executed to carry out the plan.
        :return: A TimePrediction object containing the predicted time and reasoning, or None if the prediction could not be made.
        """

        # Load personality contexts
        personalities_path = f"{self.prompt_root_path}/{self.game_subject}/personalities"
        persa_context = read_file(f"{personalities_path}/{self.personality}.txt")

        # Load main prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/time_predictor_prompt.txt"
        context = read_file(prompt_path)

        # Replace placeholders
        context = context.replace("{Personalities}", persa_context)

        # Convert the current game state to prompt input
        curr_status = generate_time_predictor_input(
            game_subject=self.game_subject,
            status=curr_status,
            plan=plan,
            result_prediction=result_prediction,
            code=code,
        )

        self.c("Query:\n", curr_status)

        # Call the language model
        time_prediction = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful assistant to predict the time required for completing a plan given the code to execute it.",
            context=context,
            question=curr_status
        )

        if not time_prediction:
            self.e("LLM response was empty. Ignore.")
            return None

        self.h("Response:\n", time_prediction)

        prediction_obj = TimePrediction(time_prediction.reasoning, time_prediction.time_prediction)

        return prediction_obj
