import json


class ResultPrediction:
    def __init__(
            self,
            prediction_reason: str,
            quantity: int,
            predicted_items: list[str] | str,
    ):
        """
        Initializes a ResultPrediction object.
        :param prediction_reason: The reason for the prediction.
        :param quantity: The quantity of the predicted item.
        :param predicted_items: The predicted item.
        """
        self.prediction_reason = prediction_reason
        self.quantity = quantity

        # Parse the items string into a list
        if isinstance(predicted_items, str):
            self.items = [item.strip() for item in predicted_items.split(",") if item.strip()]
        elif isinstance(predicted_items, list):
            self.items = predicted_items
        else:
            raise ValueError(f"items must be a string or a list, got {type(predicted_items)} instead")

    def __str__(self):
        """
        Returns a string representation of the ResultPrediction instance.
        :return: A formatted string containing prediction reason, quantity, and item.
        """
        return (
            f"ResultPrediction(prediction_reason={self.prediction_reason}, "
            f"quantity={self.quantity}, items={self.items})"
        )

    def __repr__(self):
        return self.__str__()

    def to_context_input(self) -> str:
        """
        Converts the ResultPrediction object to a string format suitable for context input.
        :return: A string representation of the ResultPrediction object.
        """
        res = ""
        for item in self.items:
            res += f"{self.quantity} {item})\n"
        return res.strip()

    def to_dict(self):
        """
        Converts the ResultPrediction object to a dictionary.
        :return: A dictionary representation of the ResultPrediction object.
        """
        return {
            "prediction_reason": self.prediction_reason,
            "quantity": self.quantity,
            "items": self.items
        }

    @classmethod
    def from_dict(cls, doc: str):
        """
        Initializes the ResultPrediction object from a dictionary.
        :param doc: A JSON string or dictionary containing the prediction details.
        :return: An instance of ResultPrediction initialized with the provided data.
        """
        data = doc if isinstance(doc, dict) else json.loads(doc)

        return cls(
            prediction_reason=data.get("prediction_reason", ""),
            quantity=data.get("quantity", 0),
            items=data.get("items", [])
        )