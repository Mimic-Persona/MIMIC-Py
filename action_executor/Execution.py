from typing import Optional, Union
import json

from action_executor.Feedback import Feedback
from hybrid_planner.Plan import Plan
from skill_system.Skill import Skill


class Execution:
    def __init__(
        self,
        plan: Plan,
        feedbacks: list[Feedback],
        is_timeout: bool = False,
        skills_created: str | list[str] = None,
        skills_used: list[str] = None,
    ):
        """
        Initializes an Execution object.
        :param plan: The plan to be executed.
        :param feedbacks: List of Feedback objects from execution.
        :param is_timeout: Boolean indicating if the execution timed out.
        :param skills_created: Optional Skill object that was created.
        :param skills_used: Optional list of Skill objects that were used.
        """
        self.plan = plan
        self.feedbacks = feedbacks
        self.is_timeout = is_timeout
        self.is_error = any(f.is_error for f in feedbacks)

        if isinstance(skills_created, str):
            self.skills_created = [skills_created]

        elif isinstance(skills_created, list):
            self.skills_created = skills_created

        else:
            self.skills_created = []

        self.skills_used = skills_used or []

    def __str__(self):
        """
        Returns a string representation of the Execution object.
        """
        return (
            f"Execution(plan={self.plan}, "
            f"skills_created={self.skills_created}, "
            f"skills_used={self.skills_used}, "
            f"feedbacks={self.feedbacks}, "
            f"is_timeout={self.is_timeout}, "
            f"is_error={self.is_error})"
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        """
        Converts the Execution object to a dictionary.
        :return: A dictionary representation of the Execution object.
        """
        return {
            "plan": self.plan.to_dict(),
            "feedbacks": [f.to_dict() for f in self.feedbacks],
            "is_timeout": self.is_timeout,
            "skills_created": self.skills_created,
            "skills_used": self.skills_used,
        }

    @classmethod
    def from_dict(cls, doc: Union[str, dict]) -> "Execution":
        """
        Initializes the Execution object from a dictionary or JSON string.
        :param doc: A JSON string or dictionary containing the execution details.
        :return: An instance of Execution initialized with the provided data.
        """
        if isinstance(doc, str):
            doc = json.loads(doc)

        plan = Plan.from_dict(doc["plan"])
        feedbacks = [Feedback.from_dict(f) for f in doc["feedbacks"]]
        is_timeout = doc.get("is_timeout", False)
        skills_created = doc.get("skills_created", [])
        skills_used = doc.get("skills_used", [])

        return cls(plan, feedbacks, is_timeout, skills_created, skills_used)