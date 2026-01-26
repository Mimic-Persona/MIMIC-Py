import json
from pydantic import BaseModel


class Decision(BaseModel):
    plan: str
    decision: bool
    reason: str = ""
    critique: str = ""

    def __str__(self):
        return f"Decision(plan={self.plan}, decision={self.decision}, reason={self.reason}, critique={self.critique})"

    def __repr__(self):
        return self.__str__()

    def to_planner_input(self) -> dict:
        """
        Converts the Decision object to a format suitable for planner input.
        :return: A dictionary containing only relevant planner fields.
        """
        return {
            "plan": self.plan,
            "reason": self.reason,
            "critique": self.critique
        }

    def to_dict(self) -> dict:
        """
        Converts the Decision object to a dictionary.
        :return: A dictionary representation of the Decision object.
        """
        return self.dict()

    @classmethod
    def from_dict(cls, doc: str | dict) -> "Decision":
        """
        Initializes the Decision object from a dictionary or JSON string.
        :param doc: A dictionary or JSON string.
        :return: A Decision instance.
        """
        data = json.loads(doc) if isinstance(doc, str) else doc
        return cls(**data)
