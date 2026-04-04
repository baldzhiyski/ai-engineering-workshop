from typing import Optional
from sqlalchemy.orm import Session
from ..db.repository.chat_repository import ChatRepository


class ShortTermMemory:
    def __init__(self) -> None:
        self.chat_repo = ChatRepository()

    def append_user_message(
        self,
        db: Session,
        session_id: str,
        content: str,
    ) -> None:
        self.chat_repo.add_message(
            db=db,
            session_id=session_id,
            role="user",
            content=content,
            message_type="chat",
        )

    def append_assistant_message(
        self,
        db: Session,
        session_id: str,
        content: str,
    ) -> None:
        self.chat_repo.add_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=content,
            message_type="chat",
        )

    def append_tool_message(
        self,
        db: Session,
        session_id: str,
        content: str,
    ) -> None:
        self.chat_repo.add_message(
            db=db,
            session_id=session_id,
            role="tool",
            content=content,
            message_type="tool",
        )

    def get_thread_messages(
        self,
        db: Session,
        session_id: str,
    ) -> list[dict]:
        return self.chat_repo.get_messages(db, session_id)