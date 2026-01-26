import json

from action_executor.Execution import Execution
from hybrid_planner.Plan import Plan
from preference_analyzer.PreferenceAnalysis import PreferenceAnalysis
from summarizer.Summary import Summary


class Memory:
    def __init__(
        self,
        memory_id: int,
        personality: str,
        prev_env: str,
        post_env: str,
        plan: Plan,
        execution: Execution,
        summary: Summary,
        preference_analysis: PreferenceAnalysis,
        time_created: float = None,
        time_accessed: float = None,
        time_expired: float = None,
    ):
        self.memory_id = memory_id
        self.personality = personality
        self.is_err_memory = execution.is_error
        self.prev_env = prev_env
        self.post_env = post_env
        self.plan = plan
        self.execution = execution
        self.summary = summary
        self.preference_analysis = preference_analysis
        self.time_created = time_created
        self.time_accessed = time_accessed
        self.time_expired = time_expired

    def __str__(self):
        return (
            f"Memory(memory_id={self.memory_id}, personality={self.personality}, "
            f"is_err_memory={self.is_err_memory}, prev_env={self.prev_env}, post_env={self.post_env}, "
            f"plan={self.plan}, execution={self.execution}, summary={self.summary}, "
            f"preference_analysis={self.preference_analysis}, "
            f"time_created={self.time_created}, time_accessed={self.time_accessed}, "
            f"time_expired={self.time_expired})"
        )

    __repr__ = __str__

    def to_planner_input(self) -> dict:
        return {
            "plan": self.plan.plan,
            "is_success": self.summary.is_success,
            "summary": self.summary.summary,
            "critique": self.summary.critique,
        }

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "personality": self.personality,
            "is_err_memory": self.is_err_memory,
            "prev_env": self.prev_env,
            "post_env": self.post_env,
            "plan": self.plan.to_dict(),
            "execution": self.execution.to_dict(),
            "summary": self.summary.to_dict(),
            "preference_analysis": self.preference_analysis.to_dict(),
            "time_created": self.time_created,
            "time_accessed": self.time_accessed,
            "time_expired": self.time_expired,
        }

    def to_chroma_record(self) -> tuple[str, dict]:
        document = json.dumps(self.to_dict(), ensure_ascii=False)
        raw_metadata = {
            "memory_id": self.memory_id,
            "personality": self.personality,
            "is_err_memory": self.is_err_memory,
            "prev_env": self.prev_env,
            "plan": getattr(self.plan, "plan", None),
            "is_success": getattr(self.summary, "is_success", None),
            "preference_level": getattr(self.preference_analysis, "preference_level", None),
            "preference_score": getattr(self.preference_analysis, "preference_score", None),
            "skills_created": str(getattr(self.execution, "skills_created", [])),
            "skills_used": str(getattr(self.execution, "skills_used", [])),
            "time_created": self.time_created,
            "time_accessed": self.time_accessed,
            "time_expired": self.time_expired,
        }

        # Filter out None values to meet ChromaDB's constraints
        metadata = {k: v for k, v in raw_metadata.items() if v is not None}

        return document, metadata

    @staticmethod
    def from_chroma_record(doc: str) -> "Memory":
        data = json.loads(doc) if isinstance(doc, str) else doc

        def safe_float(value):
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                return None

        return Memory(
            memory_id=data.get("memory_id", 0),
            personality=data.get("personality", ""),
            prev_env=data.get("prev_env", ""),
            post_env=data.get("post_env", ""),
            plan=Plan.from_dict(data.get("plan", {})),
            execution=Execution.from_dict(data.get("execution", {})),
            summary=Summary.from_dict(data.get("summary", {}), Plan.from_dict(data.get("plan", {}))),
            preference_analysis=PreferenceAnalysis.from_dict(data.get("preference_analysis", {})),
            time_created=safe_float(data.get("time_created")),
            time_accessed=safe_float(data.get("time_accessed")),
            time_expired=safe_float(data.get("time_expired")),
        )
