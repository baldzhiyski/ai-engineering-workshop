from sqlalchemy.orm import Session
from ...db.models import ChatSession, DocumentRecord


class DocumentRepository:
    def add_document(
        self,
        db: Session,
        session_id: str,
        file_name: str,
        file_path: str,
        content_type: str = "unknown",
        ingestion_status: str = "pending",
    ) -> DocumentRecord:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        doc = DocumentRecord(
            session_id_fk=session.id,
            file_name=file_name,
            file_path=file_path,
            content_type=content_type,
            ingestion_status=ingestion_status,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def update_status(
        self,
        db: Session,
        document_id: int,
        ingestion_status: str,
    ) -> DocumentRecord:
        doc = db.query(DocumentRecord).filter_by(id=document_id).first()
        if not doc:
            raise ValueError("Document not found")

        doc.ingestion_status = ingestion_status
        db.commit()
        db.refresh(doc)
        return doc