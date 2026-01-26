import os
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings


class ChromaVectorStore:
    def __init__(
        self,
        api_key: str,
        embedder: str = "text-embedding-3-small",
        collection_name: str = "mimic_docs",
        persist_directory: str = "./chroma_store",
        k: int = 5,
        is_reset: bool = True
    ):
        """
        Initializes a Chroma-based vector store with OpenAI embedding.
        """
        self.k = k
        self.api_key = api_key
        self.embedder = embedder
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=self.api_key,
            model_name=self.embedder
        )

        # self.client = chromadb.PersistentClient(path=self.persist_directory)
        settings = Settings(
            persist_directory=self.persist_directory,  # or None if you truly want ephemeral
            is_persistent=True,
            anonymized_telemetry=False,
        )

        self.client = chromadb.Client(settings=settings)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

        if is_reset:
            self.reset()

    def add_documents(
        self,
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None
    ) -> None:
        """
        Add documents to the Chroma collection.
        """
        if metadatas is None:
            metadatas = [{} for _ in documents]
        if ids is None:
            base_index = len(self.collection.get()["ids"])
            ids = [f"doc_{base_index + i}" for i in range(len(documents))]

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        print(f"[INFO] Added {len(documents)} documents to '{self.collection.name}'.")

    def retrieve(self, query: str, verbose: bool = True) -> list[str]:
        """
        Retrieve documents most relevant to the input query.
        """
        results = self.collection.query(query_texts=[query], n_results=self.k)
        docs = results.get("documents", [[]])[0]

        if verbose:
            print("=" * 60 + "\nRetrieved Documents\n" + "=" * 60)
            for i, doc in enumerate(docs):
                print(f"{i+1}. {doc}")

        return docs

    def reset(self) -> None:
        """
        Resets the Chroma collection and the physical storage directory.
        """
        if self.collection_name in self.client.list_collections():
            self.client.delete_collection(self.collection_name)

        print(f"[INFO] Collection '{self.collection_name}' has been reset.")


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    store = ChromaVectorStore(
        api_key=os.getenv("OPENAI_API_KEY"),
        embedder="text-embedding-3-small",
        collection_name="mimic_docs",
        persist_directory="../chroma_store",
        k=5
    )

    store.reset()

    store.add_documents(
        documents=[
            "Lava harms players.",
            "Use water to extinguish fire in Minecraft."
        ],
        metadatas=[
            {"topic": "danger"},
            {"topic": "tips"}
        ]
    )

    store.retrieve("Lava")
