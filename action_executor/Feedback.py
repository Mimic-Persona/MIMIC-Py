import json


class Feedback:
    def __init__(
            self,
            is_error: bool,
            message: str = ""
    ):
        """
        Initializes a Feedback object.
        :param is_error: A boolean indicating whether the feedback is an error (True) or not (False).
        :param message: An optional message providing details about the feedback.
        """
        self.is_error = is_error
        self.message = message

    def __str__(self):
        return f"Feedback(is_error={self.is_error}, message='{self.message}')"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Converts the Feedback object to a dictionary.
        :return: A dictionary representation of the Feedback object.
        """
        return {
            "is_error": self.is_error,
            "message": self.message
        }

    @classmethod
    def from_dict(cls, doc: str):
        """
        Initializes the Feedback object from a dictionary.
        :param doc: A JSON string or dictionary containing the feedback details.
        :return: An instance of Feedback initialized with the provided data.
        """
        data = doc if isinstance(doc, dict) else json.loads(doc)

        return cls(
            is_error=data.get("is_error", False),
            message=data.get("message", "")
        )

    @staticmethod
    def combine_list_of_feedbacks(
            feedbacks: list["Feedback"]
    ) -> list["Feedback"]:
        """
        Combines a list of Feedback objects into a single Feedback object.
        :param feedbacks: A list of Feedback objects to combine.
        :return: A list of two Feedback objects: one for errors and one for logs.
        """
        error_feedbacks = []
        log_feedbacks = []

        for feedback in feedbacks:
            if feedback.is_error:
                error_feedbacks.append(feedback)
            else:
                log_feedbacks.append(feedback)

        combined_feedbacks = []
        if error_feedbacks:
            combined_feedbacks.append(Feedback(is_error=True, message="\n".join(f.message for f in error_feedbacks)))
        if log_feedbacks:
            combined_feedbacks.append(Feedback(is_error=False, message="\n".join(f.message for f in log_feedbacks)))

        return combined_feedbacks