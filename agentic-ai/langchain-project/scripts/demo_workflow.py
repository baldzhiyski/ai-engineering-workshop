from ..app.db.session import SessionLocal
from ..app.db.repository.chat_repository import ChatRepository
from ..app.db.repository.workflow_repository import WorkflowRepository
from ..app.db.checkpoint.checkpointer import SimpleCheckpointer


def main():
    db = SessionLocal()
    chat_repo = ChatRepository()
    workflow_repo = WorkflowRepository()
    checkpointer = SimpleCheckpointer()

    session = chat_repo.get_or_create_session(
        db=db,
        session_id="workflow-demo",
        title="Workflow Demo",
    )

    run = workflow_repo.create_run(
        db=db,
        session_id=session.session_id,
        task_type="document_analysis",
    )

    state_step_1 = {
        "session_id": session.session_id,
        "step": "plan",
        "user_input": "Analyze uploaded incident PDFs",
        "plan": {
            "task_type": "document_analysis",
            "needs_retrieval": True,
            "needs_tools": False,
        },
    }
    checkpointer.save(db, run.id, "plan", state_step_1)

    state_step_2 = {
        "session_id": session.session_id,
        "step": "retrieve",
        "retrieved_context": "Incident A is similar to Incident B...",
    }
    checkpointer.save(db, run.id, "retrieve", state_step_2)

    workflow_repo.finish_run(
        db=db,
        workflow_run_id=run.id,
        final_answer="Root cause appears related to configuration drift.",
    )

    latest = checkpointer.load_latest(db, run.id)
    print("Latest checkpoint:")
    print(latest)

    db.close()


if __name__ == "__main__":
    main()