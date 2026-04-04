from sqlalchemy.orm import Session
from ...db.models import (ChatSession, ChatMessage)


class ChatRepository:
    def get_or_create_session(
        self,
        db: Session,
        session_id: str,
        user_id: str = "default-user",
        title: str = "Untitled Session",
    ) -> ChatSession:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if session:
            return session

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title=title,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def add_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        message_type: str = "chat",
    ) -> ChatMessage:
        session = self.get_or_create_session(db, session_id=session_id)

        message = ChatMessage(
            session_id_fk=session.id,
            role=role,
            content=content,
            message_type=message_type,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_messages(self, db: Session, session_id: str) -> list[dict]:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            return []

        messages = (
            db.query(ChatMessage)
            .filter_by(session_id_fk=session.id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "message_type": msg.message_type,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]