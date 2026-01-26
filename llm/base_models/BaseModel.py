class BaseModel:
    def __init__(
            self,
            model_name: str = "",
            model_url: str = "",
            provider: str = "",
            api_key: str = ""
    ):
        self.model_name = model_name
        self.model_url = model_url
        self.provider = provider
        self.api_key = api_key
