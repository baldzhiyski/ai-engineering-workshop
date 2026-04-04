from ..app.db.session import SessionLocal
from ..app.db.repository.chat_repository import ChatRepository

def main():
    db = SessionLocal()
    repo = ChatRepository()

    repo.get_or_create_session(
        db=db,
        session_id="demo-session",
        user_id="demo-user",
        title="Demo Session",
    )
    repo.add_message(
        db=db,
        session_id="demo-session",
        role="user",
        content="Hello, analyze my incident documents.",
    )
    repo.add_message(
        db=db,
        session_id="demo-session",
        role="assistant",
        content="Sure. Upload the files and I will help.",
    )

    db.close()
    print("Seed data inserted.")


if __name__ == "__main__":
    main()