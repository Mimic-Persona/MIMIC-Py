from typing import Any, Union
from pydantic import Field
from hybrid_planner.Plan import Plan
import json


class TopDownPlan(Plan):
    sub_plans: list[Plan] = Field(default_factory=list)

    def __str__(self):
        extras = ", ".join(f"{k}={v}" for k, v in self.extra_fields.items())
        sub_plans_str = f", sub_plans={[str(sp) for sp in self.sub_plans]}" if self.sub_plans else ""
        return f"TopDownPlan(plan={self.plan}, plan_reason={self.plan_reason}, {extras}{sub_plans_str})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict[str, Any]:
        # Recursively convert extra fields if they are Plan or TopDownPlan
        def serialize_extra(value):
            if isinstance(value, Plan):
                return value.to_dict()
            if isinstance(value, list):
                return [serialize_extra(v) for v in value]
            if isinstance(value, dict):
                return {k: serialize_extra(v) for k, v in value.items()}
            return value

        serialized_extras = {k: serialize_extra(v) for k, v in self.extra_fields.items()}

        return {
            "plan": self.plan,
            "plan_reason": self.plan_reason,
            "sub_plans": [sp.to_dict() for sp in self.sub_plans],
            **serialized_extras
        }


    @classmethod
    def from_dict(cls, doc: Union[str, dict[str, Any]]) -> "TopDownPlan":
        data = json.loads(doc) if isinstance(doc, str) else doc
        plan = data.get("plan", "")
        plan_reason = data.get("plan_reason")
        sub_plans = [Plan.from_dict(sp) for sp in data.get("sub_plans", [])]
        extra_fields = {k: v for k, v in data.items() if k not in {"plan", "plan_reason", "sub_plans"}}
        return cls(plan=plan, plan_reason=plan_reason, sub_plans=sub_plans, **extra_fields)
