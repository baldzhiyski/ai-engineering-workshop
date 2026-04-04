from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..db.repository.chat_repository import ChatRepository
from ..db.repository.document_repository import DocumentRepository

router = APIRouter(prefix="/documents", tags=["documents"])


class RegisterDocumentRequest(BaseModel):
    session_id: str
    file_path: str


def guess_content_type(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".txt":
        return "text/plain"
    if suffix == ".md":
        return "text/markdown"
    return "unknown"


@router.post("/register")
def register_document(req: RegisterDocumentRequest, db: Session = Depends(get_db)):
    chat_repo = ChatRepository()
    doc_repo = DocumentRepository()

    chat_repo.get_or_create_session(
        db=db,
        session_id=req.session_id,
        title="Document Session",
    )

    file_name = Path(req.file_path).name

    doc = doc_repo.add_document(
        db=db,
        session_id=req.session_id,
        file_name=file_name,
        file_path=req.file_path,
        content_type=guess_content_type(req.file_path),
        ingestion_status="pending",
    )

    return {
        "id": doc.id,
        "session_id": req.session_id,
        "file_name": doc.file_name,
        "file_path": doc.file_path,
        "content_type": doc.content_type,
        "ingestion_status": doc.ingestion_status,
    }