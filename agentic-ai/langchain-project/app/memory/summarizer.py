from sqlalchemy.orm import Session
from ..llms.models import get_general_model
from ..db.repository.chat_repository import ChatRepository


class SessionSummarizer:
    def __init__(self) -> None:
        self.chat_repo = ChatRepository()

    def summarize_session(
        self,
        db: Session,
        session_id: str,
    ) -> str:
        messages = self.chat_repo.get_messages(db, session_id=session_id)

        if not messages:
            return "No conversation yet."

        conversation = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages[-20:]
        )

        prompt = f"""
Summarize the following session briefly.
Focus on:
- user goal
- important facts
- unresolved items

Conversation:
{conversation}
""".strip()

        model = get_general_model()
        response = model.invoke(prompt)
        return response.content