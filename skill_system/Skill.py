import json
import os

from dotenv import load_dotenv

from utils.file_utils import read_file, write_file


class Skill:
    def __init__(
            self,
            skill_id: int,
            skill_name: str,
            skill_root_path: str,
            code: str,
            description: str,
            used_skills_ids: list[int],
            used_skills_names: list[str],
            code_language: str = "javascript",
            language_file_extension: str = ".js",
            time_created: float = None,
            time_accessed: float = None,
            time_expired: float = None,
            is_from_chroma: bool = False,
    ):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.code_language = code_language
        self.language_file_extension = language_file_extension

        self.skill_path = skill_root_path + f"/code/{skill_name}{self.language_file_extension}"
        self.description_path = skill_root_path + f"/description/{skill_name}.txt"

        if not is_from_chroma:
            write_file(self.skill_path, code)
            write_file(self.description_path, description)

        self.used_skills_ids = used_skills_ids
        self.used_skills_names = used_skills_names
        self.time_created = time_created
        self.time_accessed = time_accessed
        self.time_expired = time_expired

    def __str__(self):
        """
        Returns a string representation of the Skill object.
        :return: A string representation of the Skill object.
        """
        return (
            f"Skill(skill_id={self.skill_id}, skill_name={self.skill_name}, "
            f"skill_path={self.skill_path}, description_path={self.description_path}, "
            f"used_skills_ids={self.used_skills_ids}, used_skills_names={self.used_skills_names}, "
            f"code_language={self.code_language}, language_file_extension={self.language_file_extension}, "
            f"time_created={self.time_created}, time_accessed={self.time_accessed}, "
            f"time_expired={self.time_expired})"
        )

    __repr__ = __str__

    def get_skill_code(self) -> str:
        """
        Returns the code stored in the skill_path.
        :return: The code of the skill as a string.
        """
        return read_file(self.skill_path)

    def get_skill_description(self) -> str:
        """
        Returns the description stored in the description_path.
        :return: The description of the skill as a string.
        """
        return read_file(self.description_path)

    def to_dict(self) -> dict:
        """
        Converts the Skill object to a dictionary.
        :return: A dictionary representation of the Skill object.
        """
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "skill_path": self.skill_path,
            "description_path": self.description_path,
            "skills_used_ids": self.used_skills_ids,
            "skills_used_names": self.used_skills_names,
            "code_language": self.code_language,
            "language_file_extension": self.language_file_extension,
            "time_created": self.time_created,
            "time_accessed": self.time_accessed,
            "time_expired": self.time_expired,
        }

    def to_chroma_record(self) -> tuple[str, dict]:
        document = json.dumps(self.to_dict(), ensure_ascii=False)
        raw_metadata = {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "skill_path": self.skill_path,
            "description_path": self.description_path,
            "skills_used_ids": str(self.used_skills_ids),
            "skills_used_names": str(self.used_skills_names),
            "code_language": self.code_language,
            "language_file_extension": self.language_file_extension,
            "time_created": self.time_created,
            "time_accessed": self.time_accessed,
            "time_expired": self.time_expired,
        }

        # Filter out None values to meet ChromaDB's constraints
        metadata = {k: v for k, v in raw_metadata.items() if v is not None}

        return document, metadata

    @staticmethod
    def from_chroma_record(doc: str) -> "Skill":
        """
        Creates a Skill object from a ChromaDB record.
        :param doc: The document string from ChromaDB.
        :return: A Skill object created from the document.
        """
        data = json.loads(doc) if isinstance(doc, str) else doc

        def safe_float(value):
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                return None

        return Skill(
            skill_id=data.get("skill_id", 0),
            skill_name=data.get("skill_name", ""),
            skill_root_path=str(os.path.dirname(data.get("skill_path", "")))[:-5],  # Remove '/code'
            code=data.get("code", ""),
            description=data.get("description", ""),
            used_skills_ids=data.get("skills_used_ids", []),
            used_skills_names=data.get("skills_used_names", []),
            code_language=data.get("code_language", "javascript"),
            language_file_extension=data.get("language_file_extension", ".js"),
            time_created=safe_float(data.get("time_created")),
            time_accessed=safe_float(data.get("time_accessed")),
            time_expired=safe_float(data.get("time_expired")),
            is_from_chroma=True,
        )