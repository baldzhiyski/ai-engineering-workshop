from ...rag.retrievers import retrieval_manager
from ..state import WorkflowState

def retrieve_node(state: WorkflowState):
    if not state.plan or not state.plan.needs_retrieval:
        return {"retrieved_context": ""}

    retriever = retrieval_manager.get_retriever(k=5)
    docs = retriever.invoke(state.user_input)
    context = "".join(doc.page_content for doc in docs)
    return {"retrieved_context": context}