from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from ..api.deps import get_db
from ..memory.manager import memory_manager
from ..memory.short_term import ShortTermMemory
from ..db.repository.chat_repository import ChatRepository
from ..db.repository.workflow_repository import WorkflowRepository
from ..db.checkpoint.checkpointer import SimpleCheckpointer
from ..graphs.main import build_workflow_graph
from ..graphs.state import build_initial_state

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    session_id: str
    message: str
    task_type: str = "chat"


class ChatResponse(BaseModel):
    session_id: str
    answer: str


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    chat_repo = ChatRepository()
    short_term = ShortTermMemory()
    workflow_repo = WorkflowRepository()
    checkpointer = SimpleCheckpointer()

    # Ensure session exists
    chat_repo.get_or_create_session(
        db=db,
        session_id=req.session_id,
        title="Chat Session",
    )

    # Save user message to short-term memory
    short_term.append_user_message(db, req.session_id, req.message)

    # Load thread history
    messages = short_term.get_thread_messages(db, req.session_id)

    # Create workflow run
    workflow_run = workflow_repo.create_run(
        db=db,
        session_id=req.session_id,
        task_type=req.task_type,
    )

    # Build graph
    graph = build_workflow_graph()

    # Initial graph state
    initial_state = build_initial_state(
        user_input=req.message,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in {"user", "assistant", "tool"}
        ],
    ).model_dump()

    # Save initial checkpoint
    checkpointer.save(
        db=db,
        workflow_run_id=workflow_run.id,
        step_name="input",
        state=initial_state,
    )

    # Run graph
    logger.info("Invoking workflow graph for session=%s run_id=%s", req.session_id, workflow_run.id)
    logger.debug("Initial state=%s", initial_state)
    try:
        result = graph.invoke(initial_state)
        logger.info("Graph run completed for session=%s run_id=%s", req.session_id, workflow_run.id)
        logger.debug("Final state=%s", result)
    except Exception:
        logger.exception("Graph invocation failed for session=%s run_id=%s", req.session_id, workflow_run.id)
        raise

    # Save final checkpoint
    checkpointer.save(
        db=db,
        workflow_run_id=workflow_run.id,
        step_name="final_state",
        state=result,
    )

    final_answer = result.get("final_answer", "")

    # Finish workflow run
    workflow_repo.finish_run(
        db=db,
        workflow_run_id=workflow_run.id,
        final_answer=final_answer,
    )

    # Save assistant response
    short_term.append_assistant_message(db, req.session_id, final_answer)

    return ChatResponse(
        session_id=req.session_id,
        answer=final_answer,
    )


@router.get("/{session_id}/history")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    short_term = ShortTermMemory()
    return {
        "session_id": session_id,
        "messages": short_term.get_thread_messages(db, session_id),
    }


@router.post("/{session_id}/summarize")
def summarize_chat(session_id: str, db: Session = Depends(get_db)):
    summary = memory_manager.persist_summary(db, session_id)
    return {
        "session_id": session_id,
        "summary": summary,
    }