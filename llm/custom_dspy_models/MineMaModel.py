from llm.custom_dspy_models.CustomDspyLlmModel import CustomDspyLlmModel

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class MineMaModel(CustomDspyLlmModel):
    def __init__(
            self,
            model_name: str = "MineMA/MineMA-3-8B-v4",
            model_path: str = "/Users/nosanq/Desktop/McGill/Graduated Study/MIMIC/MIMIC v2.0 2025.3/Codes/MIMIC/Model_Fine-Tuning/models/Lamarckvergence-14B",
            signature: str = "system, context, question -> items_required, num_of_steps: int",
            temperature: float = 0.6,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        super().__init__(
            model_name=model_name,
            model_path=model_path,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

    def _load_model(self):
        super()._load_model()

        # tokenizer first
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True)

        model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            local_files_only=True,
        )

        # Patch special tokens (EOS/PAD)
        # 1) Make sure tokenizer has EOS
        if self.tokenizer.eos_token_id is None:
            # Try common EOS strings
            for tok in ["</s>", "<|endoftext|>", "<|eot_id|>"]:
                tid = self.tokenizer.convert_tokens_to_ids(tok)
                if tid is not None and tid != self.tokenizer.unk_token_id:
                    self.tokenizer.eos_token = tok
                    break

        if self.tokenizer.eos_token_id is None:
            raise ValueError(
                f"No eos_token_id found. tokenizer eos_token={self.tokenizer.eos_token!r}, "
                f"special_tokens_map={getattr(self.tokenizer, 'special_tokens_map', None)}"
            )

        # 2) PAD often missing for decoder-only: set to EOS
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        eos_id = int(self.tokenizer.eos_token_id)
        pad_id = int(self.tokenizer.pad_token_id)

        # 3) Propagate into model config and generation config
        model.config.eos_token_id = eos_id
        model.generation_config.eos_token_id = eos_id
        model.config.pad_token_id = pad_id
        model.generation_config.pad_token_id = pad_id

        print("[MineMaModel] eos_token:", self.tokenizer.eos_token, eos_id, "| pad_token:", self.tokenizer.pad_token,
              pad_id)

        return model

    def _inference(
            self,
            messages,
    ) -> str:
        """
        Generates a response from the model based on the provided messages.
        :param messages: List of dictionaries containing the conversation history.
        :return: A string containing the model's response.
        """
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)

        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        outputs = self.model.generate(
            input_ids,
            max_new_tokens=self.max_tokens,
            eos_token_id=int(self.tokenizer.eos_token_id),
            pad_token_id=int(self.tokenizer.pad_token_id),
            do_sample=True,
            temperature=self.temperature,
            top_p=0.9,
            #repetition_penalty=1.3,  # If there are duplicate problems with model responses, you can use this line of code
        )

        retry = 0
        response = ""

        while response.strip() == "" and retry < self.num_retries:
            response_ids = outputs[0][input_ids.shape[-1]:]
            response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
            retry += 1

        assert response is not None, "Failed to generate a response after retries."

        return response


if __name__ == "__main__":
    model = MineMaModel(signature="system, context, question -> answer")

    for i in range(3):

        res_dict = model.predict(
            system="As a professional assistant in Minecraft, let's think about it step by step.",
            context="Please provide me with the detailed plans, step by step, along with some descriptions.",
            question="Tell me how I could shear one sheep?",
            verbose=True,
        )

        print (f"\n====================== Sheer 1 Sheep ======================\n{res_dict}\n")

        res_dict = model.predict(
            system="As a professional assistant in Minecraft, let's think about it step by step.",
            context="Please provide me with the detailed plans, step by step, along with some descriptions.",
            question="Tell me how I could cook 1 meat (any meat is ok)?",
            verbose=True,
        )

        print (f"\n====================== Cook 1 Meat ======================\n{res_dict}\n")

        res_dict = model.predict(
            system="As a professional assistant in Minecraft, let's think about it step by step.",
            context="Please provide me with the detailed plans, step by step, along with some descriptions.",
            question="Tell me how I could mine 1 diamond?",
            verbose=True,
        )

        print (f"\n====================== Mine 1 Diamond ======================\n{res_dict}\n")

    # # Print the response for each attrs
    # print(f"Reasoning: {res_dict['reasoning']}")
    # print(f"Items Required: {res_dict['items_required']}")
    # print(f"Number of Steps: {res_dict['num_of_steps']}")
