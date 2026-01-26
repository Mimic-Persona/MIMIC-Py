from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator
import json


class Plan(BaseModel):
    plan: str
    plan_reason: Optional[str] = None
    parent_plan: Optional["Plan"] = None  # forward reference
    extra_fields: dict[str, Any] = Field(default_factory=dict)

    def __str__(self):
        base = f"Plan(plan={self.plan}, plan_reason={self.plan_reason}, "
        extras = ", ".join(f"{k}={v}" for k, v in self.extra_fields.items())
        return base + extras + ")"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "plan": self.plan,
            "plan_reason": self.plan_reason,
            "parent_plan": self.parent_plan.plan if self.parent_plan else None,
            **self.extra_fields,
        }

    @classmethod
    def from_dict(cls, doc_str: str) -> "Plan":
        data = json.loads(doc_str) if isinstance(doc_str, str) else doc_str
        return cls(**data)

    @model_validator(mode="before")
    @classmethod
    def extract_extra_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        known_fields = {"plan", "plan_reason", "parent_plan"}
        values["extra_fields"] = {
            k: v for k, v in values.items() if k not in known_fields
        }
        return values


# Required for forward references to work
Plan.update_forward_refs()
