import os
import json
import warnings
import dspy

from llm.LlmModel import LlmModel
from llm.ChromaVectorStore import ChromaVectorStore


class RAG:
    def __init__(
            self,
            model_name: str,
            model_url: str = None,
            api_key: str = None,
            temperature: float = 0.0,
            max_tokens: int = 4096,
            num_retries: int = 3,
            retriever_type: str = "vector",
            chroma_store: ChromaVectorStore = None,
            jsonl_path: str = None,
            k: int = 5,
            verbose: bool = True,
    ):
        """
        Initializes a RAG (Retrieval-Augmented Generation) model using a specified LLM and retriever.

        :param model_name: e.g., 'openai/gpt-4o'
        :param model_url: Optional URL override (e.g., localhost or proxy)
        :param api_key: API key for LLM access
        :param temperature: LLM generation temperature
        :param max_tokens: Token budget for LLM output
        :param num_retries: Retry attempts for LLM failures
        :param retriever_type: "vector" or "jsonl"
        :param chroma_store: Instance of ChromaVectorStore if using vector DB
        :param jsonl_path: Path to .jsonl file for keyword search
        :param k: Number of retrieved results
        :param verbose: Whether to print retrieved documents
        """
        self.k = k
        self.retriever_type = retriever_type
        self.verbose = verbose

        # 1. Initialize LLM
        self.llm = LlmModel(
            model_name=model_name,
            model_url=model_url,
            api_key=api_key,
            signature="system, context, question -> response",
            temperature=temperature,
            max_tokens=max_tokens,
            num_retries=num_retries
        )

        # 2. Initialize retriever
        if retriever_type == "vector":
            if chroma_store is None:
                raise ValueError("ChromaVectorStore is required for vector retriever.")
            self.retriever = lambda query: chroma_store.retrieve(query, verbose=self.verbose)

        elif retriever_type == "jsonl":
            if not jsonl_path or not os.path.isfile(jsonl_path):
                raise ValueError("A valid JSONL file must be provided.")

            with open(jsonl_path, 'r', encoding='utf-8') as f:
                self.jsonl_docs = [json.loads(line) for line in f]

            def retrieve_fn(query):
                matches = [entry for entry in self.jsonl_docs if query.lower() in str(entry).lower()]
                docs = [m.get("text", m.get("answer", str(m))) for m in matches[:self.k]]
                if self.verbose:
                    print(f"{'=' * 50} Retrieved Documents {'=' * 50}\n")
                    for i, doc in enumerate(docs):
                        print(f'{i}.\t{doc}')
                    print(f"{'=' * 50}{'=' * 21}{'=' * 50}\n")
                return docs

            self.retriever = lambda query: retrieve_fn(query)

        else:
            raise ValueError(f"Unknown retriever_type: {retriever_type}")

        # 3. Set up predictor
        self._predictor = dspy.ChainOfThought(self.llm.signature)

    @property
    def signature(self) -> str:
        return self.llm.signature

    @signature.setter
    def signature(self, value: str):
        """
        Prevents reconfiguration of the model's signature by raising a warning.
        :param value: The new signature to set.
        :return: None
        """
        warnings.warn(
            "Signature has to be `system, context, question -> response` for RAG model. ",
            UserWarning
        )

    def predict(
            self,
            system: str = "",
            question: str = "",
    ):
        """
        Predicts the response based on the retrieved context and the question.
        :param system: System prompt to guide the LLM.
        :param question: The question to ask the LLM.
        :return: The predicted response from the LLM.
        """
        return self._predictor(
            system=system,
            context=self.retriever(question),
            question=question
        )


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    from llm.ChromaVectorStore import ChromaVectorStore

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    # Create and populate vector store
    chroma_store = ChromaVectorStore(
        api_key=api_key,
        embedder="text-embedding-3-small",
        collection_name="rag_docs",
        persist_directory="../chroma_store",
        k=5
    )
    chroma_store.reset()
    chroma_store.add_documents(
        documents=["Today is Sunny", "Yesterday was Rainy"],
        metadatas=[{"topic": "today"}, {"topic": "yesterday"}],
    )

    # Initialize RAG model
    rag = RAG(
        model_name="openai/gpt-4o",
        model_url="",
        api_key=api_key,
        temperature=0.0,
        max_tokens=4096,
        num_retries=3,
        retriever_type="vector",
        chroma_store=chroma_store,
        k=5
    )

    # Make a prediction
    result = rag.predict(
        system="You are a Weather Assistant. Provide accurate weather information.",
        question="What is the weather like today? and what was it like yesterday?"
    )

    print(result.response)
