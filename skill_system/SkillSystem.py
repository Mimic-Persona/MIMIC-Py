import os

from typing import Literal
from bot_components.BotComponent import BotComponent
from hybrid_planner.Plan import Plan
from llm.ChromaVectorStore import ChromaVectorStore
from skill_system.Skill import Skill
from utils.file_utils import read_file


class SkillSystem(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            embedder: str = "text-embedding-3-small",
            collection_name: str = "skill_system",
            persist_directory: str = "./skill_system/chroma_store",
            skill_root_directory: str = "./skill_system/skill_library/MC",
            model_name: str = "openai/gpt-4o",
            model_url: str = "",
            model_provider: str = "",
            signature: str = "system, context, question -> analysis",
            temperature: float = 0,
            max_tokens: int = 4096,
            num_retries: int = 3
    ):
        """
        Initializes the MemorySystem with a personality and a Chroma vector store.
        :param embedder: The embedding model to use for vectorization of documents.
        :param collection_name: Name of the Chroma collection to store memories.
        :param persist_directory: Directory where the Chroma vector store will persist its data.
        """
        super().__init__(
            prompt_root_path=prompt_root_path,
            has_llm=False,
            code_model_name=model_name,
            code_model_url=model_url,
            code_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.k = int(os.getenv("K_OF_SKILL", 5))

        self.store = ChromaVectorStore(
            api_key=self._api_key,
            embedder=embedder,
            collection_name=collection_name + "_skill",
            persist_directory=persist_directory,
            is_reset=not self.is_inherited
        )

        self.description_store = ChromaVectorStore(
            api_key=self._api_key,
            embedder=embedder,
            collection_name=collection_name + "_skill_description",
            persist_directory=persist_directory,
            is_reset=not self.is_inherited
        )

        self.skill_root_directory = skill_root_directory
        self.basic_skill_directory = os.path.join(skill_root_directory, "basic_skills")
        self.advanced_skill_directory = os.path.join(skill_root_directory, "advanced_skills")
        self.generated_skill_directory = os.path.join(skill_root_directory, "generated_skills", self.report_prefix)

        self.h(f"Skill root directory: {self.skill_root_directory}")
        self.h(f"Basic skill directory: {self.basic_skill_directory}")
        self.h(f"Advanced skill directory: {self.advanced_skill_directory}")
        self.h(f"Generated skill directory: {self.generated_skill_directory}")

        # Initialize skill directories
        self.h("Initializing skill directories...")
        SkillSystem._initialize_skill_dir(self.basic_skill_directory)
        SkillSystem._initialize_skill_dir(self.advanced_skill_directory)
        SkillSystem._initialize_skill_dir(self.generated_skill_directory)

        self.basic_skill_names = set()  # To avoid duplicates
        self.basic_skills = self.basic_skills_to_str()

        self.skill_imports = read_file(self.skill_root_directory + f"/skill_imports{self.language_file_extension}") + "\n\n"

        self.bot_msg = f"{self.game_subject}:skill_system.SkillSystem:log:"
        self.err_msg = f"{self.game_subject}:skill_system.SkillSystem:err:"

        self.c(f"Skill System initialized with {self.count_skills()} skills.")


    @staticmethod
    def _initialize_skill_dir(
            skill_path: str
    ) -> None:
        """
        Initializes the skill directory for storing skills.
        :param skill_path: Path to the skill directory.
        :return: The path to the initialized skill directory.
        """
        os.makedirs(skill_path, exist_ok=True)
        os.makedirs(os.path.join(skill_path, "code"), exist_ok=True)
        os.makedirs(os.path.join(skill_path, "description"), exist_ok=True)

    def store_skill(
            self,
            skill: Skill
    ):
        """
        Stores a skill in the skill system.
        :param skill: Skill object to be stored.
        :return: None
        """
        doc, metadata = skill.to_chroma_record()

        self.store.add_documents(
            documents=[doc],
            metadatas=[metadata],
            ids=[str(skill.skill_id)]
        )

        self.description_store.add_documents(
            documents=[skill.get_skill_description()],
            metadatas=[{'skill_id': skill.skill_id}],
            ids=[str(skill.skill_id)]
        )

        self.c(f"Stored skill with ID {skill.skill_id} in the Skill System:\n{skill}")

    def count_skills(
            self
    ) -> int:
        """
        Counts the total number of memories stored in the memory system.
        :return: Total count of memories.
        """
        return len(self.store.collection.get()["ids"])

    def retrieve_by_id(
            self,
            skill_id: int
    ) -> Skill:
        """
        Retrieves a skill by its ID from the skill system.
        :param skill_id: The ID of the skill to retrieve.
        :return: Skill object corresponding to the given ID.
        """
        results = self.store.collection.get(ids=[str(skill_id)])
        if results["documents"]:
            return Skill.from_chroma_record(results["documents"][0])
        else:
            raise ValueError(f"Skill with ID {skill_id} not found.")

    def retrieve_names_by_ids(
            self,
            skill_ids: list[int]
    ) -> list[str]:
        """
        Retrieves skill names by their IDs from the skill system.
        :param skill_ids: List of skill IDs to retrieve names for.
        :return: List of skill names corresponding to the given IDs.
        """
        results = self.store.collection.get(ids=[str(skill_id) for skill_id in skill_ids])
        return [Skill.from_chroma_record(doc).skill_name for doc in results["documents"] if doc]

    def retrieve_ids_by_names(
            self,
            skill_names: list[str]
    ) -> list[int]:
        """
        Retrieves skill IDs by their names from the skill system.
        :param skill_names: List of skill names to retrieve IDs for.
        :return: List of skill IDs corresponding to the given names.
        """
        results = self.store.collection.get(ids=[str(name) for name in skill_names])
        return [Skill.from_chroma_record(doc).skill_id for doc in results["documents"] if doc]

    def retrieve_descriptions_by_names(
            self,
            skill_names: list[str]
    ) -> list[str]:
        """
        Retrieves skill descriptions by their names from the skill system.
        :param skill_names: List of skill names to retrieve descriptions for.
        :return: List of skill descriptions corresponding to the given names.
        """
        results = self.description_store.collection.get(ids=[str(name) for name in skill_names])
        return [doc for doc in results["documents"] if doc]

    def retrieve_by_recency(
            self,
            top_k: int = -1,
            by: Literal["created", "accessed"] = "created"
    ) -> list[Skill]:
        """
        Retrieves the most recent skills based on creation or access time.
        :param top_k: Number of top skills to retrieve.
        :param by: "created" or "accessed" to specify the time attribute for sorting.
        :return: List of Skill objects sorted by the specified time attribute.
        """
        assert by in ["created", "accessed"], "`by` must be 'created' or 'accessed'"

        if top_k < 0:
            top_k = self.k

        results = self.store.collection.get()
        key = f"time_{by}"

        docs_with_time = [
            (doc, meta, meta[key])
            for doc, meta in zip(results["documents"], results["metadatas"])
            if isinstance(meta.get(key), (int, float))  # ensure it's a valid timestamp
        ]

        # Sort by timestamp descending (most recent first)
        docs_with_time.sort(key=lambda x: x[2], reverse=True)

        return [Skill.from_chroma_record(d[0]) for d in docs_with_time[:top_k]]

    def retrieve_by_relevance(
            self,
            plan: Plan,
            top_k: int = -1
    ) -> list[Skill]:
        """
        Retrieve skills whose description is semantically similar to the input plan and plan reason.
        Uses a dedicated collection that stores skill description in the document field.
        :param plan: The Plan object containing the plan and plan reason.
        :param top_k: Number of top relevant skills to retrieve.
        :return: List of Skill objects that are relevant to the given plan.
        """
        if top_k < 0:
            top_k = self.k

        results = self.description_store.collection.query(
            query_texts=[plan.plan + ". " + plan.plan_reason],
            n_results=top_k
        )
        skill_ids = [str(meta['skill_id']) for meta in results['metadatas'][0]]

        # Lookup full memory info from the main collection
        main_results = self.store.collection.get(
            ids=skill_ids
        )

        return [Skill.from_chroma_record(doc) for doc in main_results["documents"]]

    def reset(self):
        """
        Resets the memory store by deleting and recreating the collection.
        """
        self.store.reset()
        self.description_store.reset()

    def basic_skills_to_str(
            self,
    ) -> str:
        """
        Converts the basic skills to a formatted string.
        :return: Formatted string containing basic skills.
        """

        # Get all the file paths in the basic skill directory
        skills = []
        for root, _, files in os.walk(self.basic_skill_directory + "/description"):
            for file in files:
                if not file.endswith(self.language_file_extension) and not file.endswith(".txt"):
                    continue
                if file in self.basic_skill_names:
                    continue
                self.basic_skill_names.add(file.replace(self.language_file_extension, "").replace(".txt", ""))
                skill_path = os.path.join(root, file)
                skill = read_file(str(skill_path))
                skills.append(skill)

        self.h(f"Found {len(skills)} basic skills in {self.basic_skill_directory}/description:\n{self.basic_skill_names}")

        return "\n".join(
            f"```{self.code_language}\n{skill}\n```" for skill in skills
        )

    def skills_code_to_str(
            self,
            skills: list[Skill]
    ) -> str:
        """
        Converts a list of skills to a formatted string containing their code.
        :param skills: List of Skill objects to convert.
        :return: Formatted string with code snippets for each skill.
        """
        for skill in skills:
            if not skill.skill_path:
                raise ValueError(f"Skill {skill.skill_name} has no skill path defined.")

        return "\n".join(
            f"```{self.code_language}\n{skill.get_skill_code()}\n```" for skill in skills
        )

    def skills_description_to_str(
            self,
            skills: list[Skill]
    ) -> str:
        """
        Converts a list of skills to a formatted string containing their descriptions.
        :param skills: List of Skill objects to convert.
        :return: Formatted string with code snippets for each skill.
        """
        for skill in skills:
            if not skill.description_path:
                raise ValueError(f"Skill {skill.skill_name} has no description path defined.")

        return "\n".join(
            f"```{self.code_language}\n{skill.get_skill_description()}\n```" for skill in skills
        )

    def used_skills_name_to_code(
            self,
            used_skills_name: list[str],
    ) -> str:
        """
        Converts the names of the used skills to a formatted string.
        :return: Formatted string containing the names of the used skills.
        """
        res = ""

        for skill_name in used_skills_name:
            if skill_name in self.basic_skill_names:
                # If the skill is a basic skill, retrieve its code
                skill_path = os.path.join(self.basic_skill_directory, "code", f"{skill_name}{self.language_file_extension}")
                if os.path.exists(skill_path):
                    skill_code = read_file(skill_path)
                    res += f"{skill_code}\n\n"
                else:
                    self.e(f"Basic skill code for {skill_name} not found at {skill_path}.")

            else:
                # If the skill is not a basic skill, assume it's a generated skill and retrieve its code
                skill_path = os.path.join(self.generated_skill_directory, "code", f"{skill_name}{self.language_file_extension}")
                if os.path.exists(skill_path):
                    skill_code = read_file(skill_path)
                    res += f"{skill_code}\n\n"
                else:
                    self.e(f"Generated skill code for {skill_name} not found at {skill_path}.")

        return res