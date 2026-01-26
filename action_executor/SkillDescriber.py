from bot_components.BotComponent import BotComponent
from utils.file_utils import read_file


class SkillDescriber(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> description",
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

        self.bot_msg = f"{self.game_subject}:action_executor.SkillDescriber:log:"
        self.err_msg = f"{self.game_subject}:action_executor.SkillDescriber:err:"

    def describe(
            self,
            code: str,
            verbose: bool = False,
    ) -> str | None:
        """
        Generates a description for the given code snippet using an LLM.
        :param code: The code snippet to be described.
        :return: A string containing the description of the code, or None if the description could not be generated.
        """
        # Load main prompt
        prompt_path = f"{self.prompt_root_path}/{self.game_subject}/skill_describer_prompt.txt"
        context = read_file(prompt_path)

        # Call the language model
        description = self.llm.predict(
            verbose=verbose,
            bot_msg=self.bot_msg,
            system="You are a helpful assistant who can help generate description for the given code snippet.",
            context=context,
            question=code,
        )

        if not description:
            self.e("LLM response was empty. Ignore.")
            return None

        self.h("Response:\n", description)

        if not description.description:
            raise ValueError("Description is empty. Please check the regular expression or the LLM response format.")

        return description.description
