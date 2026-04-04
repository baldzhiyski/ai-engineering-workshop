from sqlalchemy.orm import Session
from ...db.repository.workflow_repository import WorkflowRepository
from ...db.checkpoint.serializers import serialize_state, deserialize_state
from ...db.models import WorkflowCheckpoint


class SimpleCheckpointer:
    def __init__(self) -> None:
        self.workflow_repo = WorkflowRepository()

    def save(
        self,
        db: Session,
        workflow_run_id: int,
        step_name: str,
        state: dict,
    ) -> WorkflowCheckpoint:
        state_json = serialize_state(state)
        return self.workflow_repo.save_checkpoint(
            db=db,
            workflow_run_id=workflow_run_id,
            step_name=step_name,
            state_json=state_json,
        )

    def load_latest(
        self,
        db: Session,
        workflow_run_id: int,
    ) -> dict | None:
        checkpoint = (
            db.query(WorkflowCheckpoint)
            .filter_by(workflow_run_id_fk=workflow_run_id)
            .order_by(WorkflowCheckpoint.created_at.desc())
            .first()
        )
        if not checkpoint:
            return None

        return deserialize_state(checkpoint.state_json)