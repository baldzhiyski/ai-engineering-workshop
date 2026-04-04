from sqlalchemy.orm import Session
from ..db.repository.memory_repository import MemoryRepository


class LongTermMemory:
    def __init__(self) -> None:
        self.repo = MemoryRepository()

    def save_user_preference(
        self,
        db: Session,
        session_id: str,
        key: str,
        value: dict,
    ) -> None:
        self.repo.put_memory(
            db=db,
            session_id=session_id,
            namespace="user_preferences",
            memory_key=key,
            value=value,
        )

    def get_user_preference(
        self,
        db: Session,
        session_id: str,
        key: str,
    ) -> dict | None:
        return self.repo.get_memory(
            db=db,
            session_id=session_id,
            namespace="user_preferences",
            memory_key=key,
        )

    def save_session_summary(
        self,
        db: Session,
        session_id: str,
        summary: str,
    ) -> None:
        self.repo.put_memory(
            db=db,
            session_id=session_id,
            namespace="session_summaries",
            memory_key="latest_summary",
            value={"summary": summary},
        )