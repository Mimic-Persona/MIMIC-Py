import json


class TimePrediction:
    def __init__(
            self,
            reasoning: str,
            time_prediction: float,
    ):
        """
        Initializes a TimePrediction object.
        :param reasoning: The reason for the time prediction.
        :param time_prediction: The predicted time as a string.
        """
        self.prediction_reason = reasoning
        self.prediction = time_prediction

        assert isinstance(self.prediction, (float, int)), (
            f"prediction must be a float or int, got {type(self.prediction)} instead"
        )

    def __str__(self):
        """
        Returns a string representation of the TimePrediction instance.
        :return: A formatted string containing the prediction reason and predicted time.
        """
        return (
            f"TimePrediction(prediction_reason={self.prediction_reason}, "
            f"prediction={self.prediction})"
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Serializes the TimePrediction instance to a dictionary.
        :return: Dictionary with prediction reason and predicted time.
        """
        return {
            "prediction_reason": self.prediction_reason,
            "prediction": str(self.prediction)
        }

    @classmethod
    def from_dict(cls, doc: str):
        """
        Deserializes a TimePrediction object from a JSON string or dictionary.
        :param doc: JSON string or dictionary representing a TimePrediction.
        :return: A TimePrediction instance.
        """
        data = doc if isinstance(doc, dict) else json.loads(doc)

        return cls(
            reasoning=data.get("prediction_reason", ""),
            time_prediction=data.get("prediction", "0.0")
        )
