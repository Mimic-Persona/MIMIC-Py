import warnings
import dspy
import time

from utils.GLog import GLog


class LlmModel:
    def __init__(
            self,
            model_name: str,
            model_url: str = "",
            model_provider: str = "",
            api_key: str = "",
            signature: str = "system, context, question -> response",
            temperature: float = 0.0,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        """
        Initializes the LlmModel with a model name and path.
        :param model_name: Name of the model to be loaded in the form of llm_provider/llm_name (e.g., 'openai/gpt-4o').
        :param model_url: The URL points to your port where the model is hosted.
        :param model_provider: The provider of the model (e.g., 'openai', 'anthropic').
        :param api_key: Your API key for accessing the model
        :param temperature: Sampling temperature for the model.
        :param max_tokens: Maximum number of tokens to generate in the response.
        :param num_retries: Number of retries for API requests in case of failure.
        """
        self.model_name = model_name
        self.model_url = model_url
        self.api_key = api_key

        self.model = dspy.LM(model_name,
                             api_base=model_url,
                             api_key=api_key,
                             # model_provider=model_provider,
                             temperature=temperature,
                             max_tokens=max_tokens,
                             num_retries=num_retries,
                             )

        self._signature = signature
        self.set_signature(signature)

        dspy.configure(lm=self.model)

        self._cot = dspy.ChainOfThought(self._signature)

    def __setattr__(self, __name, __value):
        if __name in ("signature", "_cot"):
            super().__setattr__(__name, __value)

        elif hasattr(self, __name):
            warnings.warn(
                f"Attribute '{__name}' is already set and cannot be reassigned.",
                UserWarning
        )

        else:
            super().__setattr__(__name, __value)

    def get_signature(self):
        """
        Returns the signature of the model.
        :return: The signature string.
        """
        return self._signature

    def set_signature(self, signature: str):
        """
        Sets the signature for the model.
        :param signature: The signature string to set.
        """
        object.__setattr__(self, "signature", signature)
        object.__setattr__(self, "_cot", dspy.ChainOfThought(signature))

    def predict(
            self,
            verbose = False,
            bot_msg: str = "",
            **kwargs,
    ):
        """
        Predicts the output based on the provided keyword arguments.
        :param signature: The signature string defining the input and output keys.
        :param verbose: If True, print the generated messages for debugging.
        :param bot_msg: A message prefix for logging.
        :param kwargs: Keyword arguments that match the input keys defined in the signature.
        :return:
        """
        GLog.h(f"{bot_msg} Signature set to: {self.get_signature()}")

        if verbose:
            # Print the generated messages for debugging
            print("Generated Context:")
            for key, value in kwargs.items():
                print(f"\n{key}:\n{value}\n")

            start_time = time.time()
            GLog.h(f"{bot_msg} {'=' * 20} Predicting {'=' * 20}")
            res = self._cot(**kwargs)
            end_time = time.time()
            GLog.h(f"{bot_msg} {'=' * 20} Prediction completed in {end_time - start_time:.2f} seconds {'=' * 20}")
            return res

        return self._cot(**kwargs)


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    llm = LlmModel(model_name="openai/gpt-4o",
                   model_url="",
                   api_key=api_key,
                   signature="system, context, question -> response",
                   temperature=0,
                   max_tokens=4096,
                   num_retries=3)

    print(llm.predict(system="You are a helpful assistant.",
                      context="The weather is sunny today.",
                      question="What is the weather like?"))
