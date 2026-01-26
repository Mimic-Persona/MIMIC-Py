import torch

from llm.custom_dspy_models.CustomDspyLlmModel import CustomDspyLlmModel

from transformers import AutoTokenizer, AutoModelForCausalLM

from utils.utils import system_say


class HuggingFaceLlmModel(CustomDspyLlmModel):
    def __init__(
            self,
            model_name: str = "Saxo/Linkbricks-Horizon-AI-Avengers-V1-32B",
            model_path: str = "Saxo/Linkbricks-Horizon-AI-Avengers-V1-32B",
            signature: str = "system, context, question -> items_required, num_of_steps: int",
            temperature: float = 0.1,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        super().__init__(
            model_name=model_name,
            model_path=model_path,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

    def _load_model(self):
        """
        Load the model from the specified path.
        This method is called during initialization to set up the model for inference.
        """
        super()._load_model()
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path
        )
        model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
        )

        # Patch token ids after loading
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token or "<pad>"
            self.tokenizer.pad_token_id = self.tokenizer.convert_tokens_to_ids(self.tokenizer.pad_token)

        model.config.pad_token_id = self.tokenizer.pad_token_id
        model.config.eos_token_id = self.tokenizer.eos_token_id

        if next(model.parameters()).device != self.device:
            print(f"[INFO] Moving model to {self.device}...")
            model.to(self.device)

        system_say(f"Model {self.model_name} loaded successfully on {self.device}.")

        return model

    def _inference(self, messages) -> str:
        print(f"[INFO] Running inference on: {self.device}")
        self.model.to(self.device)

        # Tokenize and move inputs to a device
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)

        # Manually create attention mask
        attention_mask = torch.ones_like(input_ids, dtype=torch.long).to(self.device)

        # Handle multiple eos tokens safely
        terminators = list(filter(
            lambda x: x is not None,
            [
                self.tokenizer.eos_token_id,
                self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]
        ))
        if not terminators:
            raise ValueError("No valid eos_token_id found. Check your tokenizer config.")

        # Generate output
        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=self.max_tokens,
            eos_token_id=terminators,
            do_sample=True,
            temperature=self.temperature,
        )

        # Decode response
        retry = 0
        response = ""
        while response.strip() == "" and retry < self.num_retries:
            response_ids = outputs[0][input_ids.shape[-1]:]
            response = self.tokenizer.decode(response_ids, skip_special_tokens=True)
            retry += 1

        assert response is not None, "Failed to generate a response after retries."
        return response


if __name__ == "__main__":

    names = [
        # "Saxo/Linkbricks-Horizon-AI-Avengers-V1-32B",
        # "fluently-lm/FluentlyLM-Prinum",
        # "JungZoona/T3Q-qwen2.5-14b-v1.0-e3",
        "zetasepic/Qwen2.5-32B-Instruct-abliterated-v2",
        # "CombinHorizon/zetasepic-abliteratedV2-Qwen2.5-32B-Inst-BaseMerge-TIES",
        # "maldv/Awqward2.5-32B-Instruct",
        # "Qwen/Qwen2.5-32B-Instruct",
        # "Saxo/Linkbricks-Horizon-AI-Avengers-V3-32B",
        # "Saxo/Linkbricks-Horizon-AI-Avengers-V6-32B",
        # "tanliboy/lambda-qwen2.5-32b-dpo-test",
    ]

    for model_name in names:
        model = HuggingFaceLlmModel(
            model_name=model_name,
            model_path=model_name,
            signature="system, context, question -> answer"
        )

    #     res_dict = model.predict(
    #         system="As a professional assistant in Minecraft, let's think about it step by step.",
    #         context="Please provide me with the detailed plans, step by step, along with some descriptions.",
    #         question="Tell me how I could shear one sheep?",
    #         verbose=True,
    #     )
    #     print (f"\n====================== Sheer 1 Sheep ======================\n{res_dict}\n")

        # for i in range(3):
        #     res_dict = None
        #     while not res_dict:
        #         try:
        #             res_dict = model.predict(
        #                 system="As a professional assistant in Minecraft, let's think about it step by step.",
        #                 context="Please provide me with the detailed plans, step by step, along with some descriptions.",
        #                 question="Tell me how I could shear one sheep?",
        #                 verbose=True,
        #             )
        #             print (f"\n====================== Sheer 1 Sheep - {i} ======================\n{res_dict}\n")
        #         except Exception as e:
        #             res_dict = None
        #
        # for i in range(3):
        #     res_dict = None
        #     while not res_dict:
        #         try:
        #             res_dict = model.predict(
        #                 system="As a professional assistant in Minecraft, let's think about it step by step.",
        #                 context="Please provide me with the detailed plans, step by step, along with some descriptions.",
        #                 question="Tell me how I could cook 1 meat (any meat is ok)?",
        #                 verbose=True,
        #             )
        #             print (f"\n====================== Cook 1 Meat - {i} ======================\n{res_dict}\n")
        #         except Exception as e:
        #             res_dict = None

        for i in range(2):
            res_dict = None
            while not res_dict:
                try:
                    res_dict = model.predict(
                        system="As a professional assistant in Minecraft, let's think about it step by step.",
                        context="Please provide me with the detailed plans, step by step, along with some descriptions.",
                        question="Tell me how I could mine 1 diamond?",
                        verbose=True,
                    )
                    print (f"\n====================== Mine 1 Diamond - {i} ======================\n{res_dict}\n")
                except Exception as e:
                    res_dict = None

    # # Print the response for each attrs
    # print(f"Reasoning: {res_dict['reasoning']}")
    # print(f"Items Required: {res_dict['items_required']}")
    # print(f"Number of Steps: {res_dict['num_of_steps']}")
