from langchain_community.vectorstores import FAISS
from ..llms.embeddings import get_embeddings


def build_vectorstore(chunks):
    return FAISS.from_documents(chunks, get_embeddings())