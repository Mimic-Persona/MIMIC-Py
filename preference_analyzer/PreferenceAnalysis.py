import json
from typing import Union

from action_executor.Execution import Execution
from hybrid_planner.Plan import Plan
from utils.file_utils import read_file


class PreferenceAnalysis:
    def __init__(
        self,
        plan: Plan,
        execution: Execution,
        analysis_path: str,
        preference_level: int,
        preference_score: float,
    ):
        """
        Initializes a PreferenceAnalysis object.
        :param plan: The Plan object associated with this analysis.
        :param execution: A list of Execution objects tied to this plan.
        :param analysis_path: The path to the text file containing the analysis summary.
        :param preference_level: An integer representing the preference level (0-5).
        :param preference_score: A float representing the computed preference score.
        """
        self.plan = plan
        self.execution = execution
        self.analysis_path = analysis_path
        self.analysis = read_file(analysis_path)
        self.preference_level = preference_level
        self.preference_score = preference_score

    def __str__(self) -> str:
        """
        Returns a string representation of the PreferenceAnalysis instance.
        :return: A formatted string containing plan, execution, analysis path, and preference level.
        """
        return (
            f"PreferenceAnalysis(plan={self.plan}, execution={self.execution}, "
            f"analysis_path={self.analysis_path}, preference_level={self.preference_level}, "
            f"preference_score={self.preference_score})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        """
        Serializes the PreferenceAnalysis instance to a dictionary.
        :return: Dictionary with plan, executions, analysis path, and preference level.
        """
        return {
            "plan": self.plan.to_dict(),
            "execution": self.execution.to_dict(),
            "analysis_path": self.analysis_path,
            "preference_level": self.preference_level,
            "preference_score": self.preference_score,
        }

    @classmethod
    def from_dict(cls, doc: Union[str, dict]) -> "PreferenceAnalysis":
        """
        Deserializes a PreferenceAnalysis object from a JSON string or dictionary.
        :param doc: JSON string or dictionary representing a PreferenceAnalysis.
        :return: A PreferenceAnalysis instance.
        """
        data = json.loads(doc) if isinstance(doc, str) else doc
        return cls(
            plan=Plan.from_dict(data.get("plan", {})),
            execution=Execution.from_dict(data.get("execution", {})),
            analysis_path=data.get("analysis_path", ""),
            preference_level=data.get("preference_level", 0),
            preference_score=data.get("preference_score", 0.0),
        )
