import json


class Code:
    def __init__(
            self,
            code_design: str,
            skill_name: str,
            used_skills_name: list[str],
            code: str,
            code_failing_reason: str = "",
    ):
        """
        Initializes a Code object.
        :param code_design: The design of the code.
        :param skill_name: Name of the skill associated with the code.
        :param used_skills_name: List of names of skills used by this code.
        :param code: The actual code as a string.
        :param code_failing_reason: Reason for any failure in the code, if applicable.
        """
        self.code_design = code_design
        self.skill_name = skill_name
        self.used_skills_name = used_skills_name
        self.code = code
        self.code_failing_reason = code_failing_reason

    def __str__(self):
        """
        Returns a string representation of the Code instance.
        :return: A formatted string containing code design, skill name, used skills, and code.
        """
        return (
            f"Code(code_design='{self.code_design}', skill_name='{self.skill_name}', "
            f"used_skills_name={self.used_skills_name}, code='{self.code}', "
            f"code_failing_reason='{self.code_failing_reason}')"
        )

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Converts the Code object to a dictionary.
        :return: A dictionary representation of the Code object.
        """
        return {
            "code_design": self.code_design,
            "skill_name": self.skill_name,
            "used_skills_name": self.used_skills_name,
            "code": self.code,
            "code_failing_reason": self.code_failing_reason
        }

    @classmethod
    def from_dict(cls, doc: str):
        """
        Initializes the Code object from a dictionary.
        :param doc: A JSON string or dictionary containing the code details.
        :return: An instance of Code initialized with the provided data.
        """
        data = doc if isinstance(doc, dict) else json.loads(doc)

        return cls(
            code_design=data.get("code_design", ""),
            skill_name=data.get("skill_name", ""),
            used_skills_name=data.get("used_skills_name", []),
            code=data.get("code", ""),
            code_failing_reason=data.get("code_failing_reason", "")
        )
