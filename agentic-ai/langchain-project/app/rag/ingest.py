from ..rag.loaders import load_documents
from ..rag.splitters import split_documents
from ..rag.vectorstores import build_vectorstore
from ..rag.retrievers import retrieval_manager


def ingest_file(path: str) -> dict:
    docs = load_documents(path)
    chunks = split_documents(docs)
    vectorstore = build_vectorstore(chunks)

    retrieval_manager.set_vectorstore(vectorstore)

    return {
        "status": "success",
        "documents_loaded": len(docs),
        "chunks_created": len(chunks),
    }