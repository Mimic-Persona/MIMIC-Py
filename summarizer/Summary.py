import json
from pydantic import BaseModel
from typing import Union
from hybrid_planner.Plan import Plan


class Summary():
    plan: Plan
    summary: str
    is_success: bool
    critique: str

    def __init__(
            self,
            plan: Plan,
            summary: str,
            is_success: bool,
            critique: str = "",
    ):
        """
        Initializes a Summary object.
        :param plan: The plan that was executed.
        :param summary: The summary of the execution.
        :param is_success: Indicates if the execution was successful.
        :param critique: Optional critique of the execution.
        """
        self.plan = plan
        self.summary = summary
        self.is_success = is_success
        self.critique = critique or ""

        assert isinstance(self.plan, Plan), f"plan must be a Plan object, got {type(self.plan)} instead"
        assert isinstance(self.is_success, bool), f"is_success must be a boolean, got {type(self.is_success)} instead"

    def __str__(self):
        return (
            f"Summary(summary={self.summary}, is_success={self.is_success}, "
            f"critique={self.critique})"
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        """
        Converts the Summary object to a dictionary.
        """
        return {
            "plan": self.plan.to_dict(),
            "summary": self.summary,
            "is_success": self.is_success,
            "critique": self.critique,
        }

    @classmethod
    def from_dict(cls, doc: Union[str, dict], plan: Plan) -> "Summary":
        data = json.loads(doc) if isinstance(doc, str) else doc
        return cls(
            plan=plan,
            summary=data.get("summary", ""),
            is_success=data.get("is_success", False),
            critique=data.get("critique") or ""
        )
