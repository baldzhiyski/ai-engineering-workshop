from sqlalchemy.orm import Session
from ..memory.short_term import ShortTermMemory
from ..memory.summarizer import SessionSummarizer
from ..memory.long_term import LongTermMemory


class MemoryManager:
    def __init__(self) -> None:
        self.short_term = ShortTermMemory()
        self.summarizer = SessionSummarizer()
        self.long_term = LongTermMemory()

    def record_turn(
        self,
        db: Session,
        session_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        self.short_term.append_user_message(db, session_id, user_message)
        self.short_term.append_assistant_message(db, session_id, assistant_message)

    def persist_summary(
        self,
        db: Session,
        session_id: str,
    ) -> str:
        summary = self.summarizer.summarize_session(db, session_id)
        self.long_term.save_session_summary(db, session_id, summary)
        return summary


memory_manager = MemoryManager()