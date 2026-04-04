from datetime import datetime
from sqlalchemy.orm import Session
from ...db.models import ChatSession, WorkflowRun, WorkflowCheckpoint


class WorkflowRepository:
    def create_run(
        self,
        db: Session,
        session_id: str,
        task_type: str = "general",
    ) -> WorkflowRun:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        run = WorkflowRun(
            session_id_fk=session.id,
            task_type=task_type,
            status="running",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def save_checkpoint(
        self,
        db: Session,
        workflow_run_id: int,
        step_name: str,
        state_json: str,
    ) -> WorkflowCheckpoint:
        checkpoint = WorkflowCheckpoint(
            workflow_run_id_fk=workflow_run_id,
            step_name=step_name,
            state_json=state_json,
        )
        db.add(checkpoint)
        db.commit()
        db.refresh(checkpoint)
        return checkpoint

    def finish_run(
        self,
        db: Session,
        workflow_run_id: int,
        final_answer: str,
    ) -> WorkflowRun:
        run = db.query(WorkflowRun).filter_by(id=workflow_run_id).first()
        if not run:
            raise ValueError("Workflow run not found")

        run.status = "completed"
        run.final_answer = final_answer
        run.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(run)
        return run

    def fail_run(
        self,
        db: Session,
        workflow_run_id: int,
        error_message: str,
    ) -> WorkflowRun:
        run = db.query(WorkflowRun).filter_by(id=workflow_run_id).first()
        if not run:
            raise ValueError("Workflow run not found")

        run.status = "failed"
        run.error_message = error_message
        run.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(run)
        return run