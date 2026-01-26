import os

from typing import Literal
from bot_components.BotComponent import BotComponent
from llm.ChromaVectorStore import ChromaVectorStore
from memory_system.Memory import Memory


class MemorySystem(BotComponent):
    def __init__(
            self,
            prompt_root_path: str,
            embedder: str = "text-embedding-3-small",
            collection_name: str = "memory_system",
            persist_directory: str = "./memory_system/chroma_store",
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
            instruction_model_name=model_name,
            instruction_model_url=model_url,
            instruction_model_provider=model_provider,
            signature=signature,
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        self.k = int(os.getenv("K_OF_MEMORY", 5))

        self.store = ChromaVectorStore(
            api_key=self._api_key,
            embedder=embedder,
            collection_name=collection_name + "_memo",
            persist_directory=persist_directory,
            is_reset=not self.is_inherited
        )

        self.env_store = ChromaVectorStore(
            api_key=self._api_key,
            embedder=embedder,
            collection_name=collection_name + "_env",
            persist_directory=persist_directory,
            is_reset=not self.is_inherited
        )

        self.bot_msg = f"{self.game_subject}:memory_system.MemorySystem:log:"
        self.err_msg = f"{self.game_subject}:memory_system.MemorySystem:err:"

        self.c(f"Memory System initialized with {self.count_memories()} memories.")

    def store_memory(
            self,
            memory: Memory
    ):
        """
        Stores a Memory object in the Chroma vector store.
        :param memory: Memory object to be stored.
        :return: None
        """
        doc, metadata = memory.to_chroma_record()

        self.store.add_documents(
            documents=[doc],
            metadatas=[metadata],
            ids=[str(memory.memory_id)]
        )

        self.env_store.add_documents(
            documents=[memory.prev_env],
            metadatas=[{'memory_id': memory.memory_id}],
            ids=[str(memory.memory_id)]
        )

        self.c(f"Stored memory with ID {memory.memory_id} in the Memory System:\n{memory}")

    def count_memories(
            self
    ) -> int:
        """
        Counts the total number of memories stored in the memory system.
        :return: Total count of memories.
        """
        return len(self.store.collection.get()["ids"])

    def count_error_memories(
            self
    ) -> int:
        """
        Counts the number of memories that are marked as error memories.
        :return: Count of error memories.
        """
        return len(self.retrieve_error_memories())

    def count_non_error_memories(
            self
    ) -> int:
        """
        Counts the number of memories that are not marked as error memories.
        :return: Count of non-error memories.
        """
        return len(self.retrieve_non_error_memories())

    def retrieve_by_id(
            self,
            memory_id: int
    ) -> Memory:
        """
        Retrieves a memory by its unique ID.
        :param memory_id: Unique identifier of the memory to retrieve.
        :return: Memory object corresponding to the provided ID.
        """
        results = self.store.collection.get(ids=[str(memory_id)])
        if results["documents"]:
            return Memory.from_chroma_record(results["documents"][0])
        else:
            raise ValueError(f"Memory with ID {memory_id} not found.")

    def retrieve_by_personality(
            self,
            personality: str
    ) -> list[Memory]:
        """
        Retrieves memories associated with a specific personality.
        :param personality: The personality string to filter memories by.
        :return: List of Memory objects associated with the specified personality.
        """
        results = self.store.collection.get()
        docs_with_personality = [
            (doc, meta) for doc, meta in zip(results["documents"], results["metadatas"])
            if meta.get("personality") == personality
        ]
        return [Memory.from_chroma_record(d[0]) for d in docs_with_personality]

    def _retrieve_by_is_error(
            self,
            is_error: bool
    ) -> list[Memory]:
        """
        Retrieves memories based on whether they are error memories or not.
        :param is_error: Boolean indicating whether to retrieve error memories (True) or non-error memories (False).
        :return: List of Memory objects filtered by the error status.
        """
        results = self.store.collection.get()
        docs_with_error_status = [
            (doc, meta) for doc, meta in zip(results["documents"], results["metadatas"])
            if Memory.from_chroma_record(doc).is_err_memory == is_error
        ]
        return [Memory.from_chroma_record(d[0]) for d in docs_with_error_status]

    def retrieve_error_memories(
            self
    ) -> list[Memory]:
        """
        Retrieves all memories that are marked as error memories.
        :return: List of Memory objects that are error memories.
        """
        return self._retrieve_by_is_error(is_error=True)

    def retrieve_non_error_memories(
            self
    ) -> list[Memory]:
        """
        Retrieves all memories that are not marked as error memories.
        :return: List of Memory objects that are non-error memories.
        """
        return self._retrieve_by_is_error(is_error=False)

    def _retrieve_by_memory_success(
            self,
            is_success: bool
    ) -> list[Memory]:
        """
        Retrieves memories based on whether they are successful or not.
        :param is_success: Boolean indicating whether to retrieve successful memories (True) or unsuccessful memories (False).
        :return: List of Memory objects filtered by the success status.
        """
        results = self.store.collection.get()
        docs_with_success_status = [
            (doc, meta) for doc, meta in zip(results["documents"], results["metadatas"])
            if Memory.from_chroma_record(doc).summary.is_success == is_success
        ]
        return [Memory.from_chroma_record(d[0]) for d in docs_with_success_status]

    def retrieve_successful_memories(
            self
    ) -> list[Memory]:
        """
        Retrieves all memories that are marked as successful.
        :return: List of Memory objects that are successful.
        """
        return self._retrieve_by_memory_success(is_success=True)

    def retrieve_unsuccessful_memories(
            self
    ) -> list[Memory]:
        """
        Retrieves all memories that are marked as unsuccessful.
        :return: List of Memory objects that are unsuccessful.
        """
        return self._retrieve_by_memory_success(is_success=False)

    def retrieve_by_recency(
            self,
            top_k: int = -1,
            by: Literal["created", "accessed"] = "created"
    ) -> list[Memory]:
        """
        Retrieves memories based on recency of creation or access using UNIX timestamp.
        :param top_k: Number of top memories to retrieve.
        :param by: "created" or "accessed" to specify the time attribute for sorting.
        :return: List of Memory objects sorted by the specified time attribute.
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

        return [Memory.from_chroma_record(d[0]) for d in docs_with_time[:top_k]]

    def retrieve_by_preference(
            self,
            top_k: int = -1,
            by: Literal["level", "score"] = "score"
    ) -> list[Memory]:
        """
        Retrieves memories based on preference level.
        :param top_k: Number of top memories to retrieve based on preference.
        :param by: "level" or "score" to specify the preference attribute for sorting.
        :return: List of Memory objects sorted by preference level.
        """
        assert by in ["level", "score"], "`by` must be 'level' or 'score'"

        if top_k < 0:
            top_k = self.k

        results = self.store.collection.get()
        docs_with_pref = [
            (doc, meta, meta.get(f"preference_{by}", 0))
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]
        docs_with_pref.sort(key=lambda x: x[2], reverse=True)
        return [Memory.from_chroma_record(d[0]) for d in docs_with_pref[:top_k]]

    def retrieve_by_relevance(
            self,
            env: str,
            top_k: int = -1
    ) -> list[Memory]:
        """
        Retrieve memories whose prev_env is semantically similar to the input env.
        Uses a dedicated collection that stores prev_env in the document field.
        :param env: The environment strings to query against.
        :param top_k: Number of top similar memories to retrieve.
        :return: List of Memory objects whose prev_env is similar to the input env.
        """
        if top_k < 0:
            top_k = self.k

        results = self.env_store.collection.query(
            query_texts=[env],
            n_results=top_k
        )
        memory_ids = [str(meta['memory_id']) for meta in results['metadatas'][0]]

        # Retrieve the main memory documents using the IDs obtained from the env store
        main_results = self.store.collection.get(
            ids=memory_ids
        )

        return [Memory.from_chroma_record(doc) for doc in main_results["documents"]]

    def reset(self):
        """
        Resets the memory store by deleting and recreating the collection.
        """
        self.store.reset()
        self.env_store.reset()

    def is_action_same_as_last(self) -> bool:
        """
        Check if the last two memories have the same extra fields in their plans.
        Returns True if all non-core fields ('plan', 'plan_reason', 'parent_plan') are identical.
        """
        if self.count_memories() < 2:
            return False

        last_memory = self.retrieve_by_id(self.count_memories() - 1)
        second_last_memory = self.retrieve_by_id(self.count_memories() - 2)

        last_plan = last_memory.plan
        second_last_plan = second_last_memory.plan

        known_fields = {"plan", "plan_reason", "parent_plan"}

        last_extras = {k: v for k, v in last_plan.__dict__.items() if k not in known_fields}
        second_last_extras = {k: v for k, v in second_last_plan.__dict__.items() if k not in known_fields}

        return last_extras == second_last_extras
