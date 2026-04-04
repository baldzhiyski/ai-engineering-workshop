from ..llms.models import get_reasoning_model
from ..rag.retrievers import retrieval_manager


def ask_rag(question: str, k: int = 5) -> dict:
    retriever = retrieval_manager.get_retriever(k=k)
    docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in docs)

    model = get_reasoning_model()

    prompt = f"""
You are a grounded assistant.
Answer the question only from the context below.
If the answer is not in the context, say you do not know.

Context:
{context}

Question:
{question}
""".strip()

    response = model.invoke(prompt)

    return {
        "answer": response.content,
        "sources": [doc.metadata for doc in docs],
    }