from typing import Optional
from langchain_community.vectorstores import FAISS


class RetrievalManager:
    def __init__(self) -> None:
        self.vectorstore: Optional[FAISS] = None

    def set_vectorstore(self, vectorstore: FAISS) -> None:
        self.vectorstore = vectorstore

    def get_retriever(self, k: int = 5):
        if self.vectorstore is None:
            raise ValueError("Vectorstore is not initialized")

        return self.vectorstore.as_retriever(search_kwargs={"k": k})


retrieval_manager = RetrievalManager()