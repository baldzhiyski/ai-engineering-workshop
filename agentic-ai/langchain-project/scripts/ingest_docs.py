import os
from pathlib import Path
from ..app.db.session import SessionLocal
from ..app.db.repository.chat_repository import ChatRepository
from ..app.db.repository.document_repository import DocumentRepository
from ..app.rag.ingest import ingest_file


DOCS_DIR = Path("data/docs")
SESSION_ID = "demo-session"


def guess_content_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".txt":
        return "text/plain"
    if suffix == ".md":
        return "text/markdown"
    return "unknown"


def main():
    db = SessionLocal()
    chat_repo = ChatRepository()
    doc_repo = DocumentRepository()

    chat_repo.get_or_create_session(
        db=db,
        session_id=SESSION_ID,
        title="Document Ingestion Session",
    )

    if not DOCS_DIR.exists():
        print(f"Directory does not exist: {DOCS_DIR}")
        db.close()
        return

    for file in DOCS_DIR.iterdir():
        if not file.is_file():
            continue

        doc = doc_repo.add_document(
            db=db,
            session_id=SESSION_ID,
            file_name=file.name,
            file_path=str(file.resolve()),
            content_type=guess_content_type(file),
            ingestion_status="pending",
        )

        try:
            ingest_file(str(file.resolve()))
            doc_repo.update_status(
                db=db,
                document_id=doc.id,
                ingestion_status="ingested",
            )
            print(f"Ingested: {file.name}")
        except Exception as exc:
            doc_repo.update_status(
                db=db,
                document_id=doc.id,
                ingestion_status=f"failed: {exc}",
            )
            print(f"Failed: {file.name} -> {exc}")

    db.close()


if __name__ == "__main__":
    main()