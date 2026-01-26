import json
import time
from typing import Dict, Any

from utils.GLog import GLog


class CustomDspyLlmModel:
    def __init__(
            self,
            model_name: str,
            model_path: str,
            signature: str = "system, context, question -> response",
            temperature: float = 0.0,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        self.model_name = model_name
        self.model_path = model_path

        self._signature = signature
        self.set_signature(signature)

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_retries = num_retries

        self.model = self._load_model()

    def _load_model(self):
        # Placeholder for loading the model
        print(f"Loading model {self.model_name} from {self.model_path}")

    def _generate_messages(
            self,
            is_cot: bool = True,
            **kwargs
    ) -> list[dict[str, str] | dict[str, str]]:
        """
        Generates a list of messages for the model based on the provided keyword arguments.
        :param kwargs: Keyword arguments that match the input keys defined in the signature.
        :return: List of dictionaries representing the messages to be sent to the model.
        """
        # Check if all required input keys are provided
        for key in self.input_keys:
            if key not in kwargs:
                raise ValueError(f"Missing required input: {key}")

        # If having a system message, use it
        sys_msg = kwargs.get("system", "You are a helpful assistant.")

        # Combine the rest of the inputs into a user message
        user_msg = "\n".join(f"{key}:\n{kwargs[key]}" for key in self.input_keys if key != "system" and key in kwargs)

        if is_cot:
            user_msg += "\n\nPlease think step by step and provide your reasoning before giving the final answer."

        user_msg += "\n\nReturn your answer as:"

        out_keys = self.output_keys
        out_types = self.output_types

        if is_cot:
            out_keys = ["reasoning"] + self.output_keys[:]
            out_types = ["str"] + self.output_types[:]

        user_msg += "\n{\n" + ",\n".join(f'"{key}": <{key_type}>' for key, key_type in zip(out_keys, out_types)) + "\n}\n"

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg}
        ]

        return messages

    def _inference(
            self,
            messages
    ) -> str:
        # Placeholder for loading the model
        raise NotImplementedError("The inference method should be implemented to call the model's predict function.")

    def _cot(
            self,
            verbose: bool = False,
            bot_msg: str = "",
            **kwargs
    ) -> dict[Any, int | float | bool | Any]:
        messages = self._generate_messages(**kwargs)

        if verbose:
            # Print the generated messages for debugging
            print("Generated messages for COT:")
            for msg in messages:
                print(f"{msg['role']}: {msg['content']}")
            start_time = time.time()
            GLog.h(f"{bot_msg} {'=' * 20} Predicting {'=' * 20}")

        # Call the model's predict method with the generated messages
        response = self._inference(messages)

        if verbose:
            end_time = time.time()
            GLog.h(f"{bot_msg} {'=' * 20} Prediction completed in {end_time - start_time:.2f} seconds {'=' * 20}")

        # Parse the response from JSON string format to a dictionary
        result = {}
        output_keys = ["reasoning"] + self.output_keys[:]
        output_types = ["str"] + self.output_types[:]

        output_keys.insert(0, "reasoning")
        output_types.insert(0, "str")

        response = response.strip()

        print(f"Raw response: {response}")

        # Only take the one from first { to the last }
        response = response[response.index("{"):response.rindex("}") + 1]

        # Parse the response as a dictionary
        try:
            response = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse response as JSON: {e}")

        for key, value in response.items():
            if key in output_keys:
                index = output_keys.index(key)
                if output_types[index] == "int":
                    result[key] = int(value)
                elif output_types[index] == "float":
                    result[key] = float(value)
                elif output_types[index] == "bool":
                    if isinstance(value, str) and value.lower() in ["true", "false"]:
                        result[key] = value.lower() == "true"
                    elif isinstance(value, bool):
                        result[key] = value
                else:
                    result[key] = value
            else:
                raise ValueError(f"Unexpected output key: {key}")

        # Transform the dictionary to an object with attributes
        return result

    def get_signature(self) -> str:
        """
        Returns the signature of the model.
        :return: The signature string.
        """
        return self._signature

    def set_signature(self, signature: str):
        """
        Sets the input and output keys based on the provided signature.
        :param signature: A string defining the input and output keys in the format "input1, input2 -> output1, output2".
        """
        self._signature = signature

        input_part, output_part = self._signature.split("->")
        self.input_keys = [k.strip() for k in input_part.split(",")]
        output_keys = [k.strip() for k in output_part.split(",")]

        self.output_keys = []
        self.output_types = []

        for i in range(len(output_keys)):
            if ":" in output_keys[i]:
                output_key, output_type = output_keys[i].split(":")

            else:
                output_key = output_keys[i]
                output_type = "str"

            self.output_keys.append(output_key.strip())
            self.output_types.append(output_type.strip())

    def predict(
            self,
            verbose: bool = False,
            **kwargs
    ) -> dict[Any, int | float | bool | Any]:
        """
        Predicts the output based on the provided keyword arguments.
        :param verbose: If True, prints the generated messages for debugging.
        :param kwargs: Keyword arguments that match the input keys defined in the signature.
        :return: An object with attributes corresponding to the output keys.
        """
        return self._cot(verbose=verbose, **kwargs)