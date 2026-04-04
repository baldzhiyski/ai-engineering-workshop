import json
from datetime import datetime
from sqlalchemy.orm import Session
from ...db.models import ChatSession, LongTermMemoryRecord


class MemoryRepository:
    def put_memory(
        self,
        db: Session,
        session_id: str,
        namespace: str,
        memory_key: str,
        value: dict,
    ) -> LongTermMemoryRecord:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        record = (
            db.query(LongTermMemoryRecord)
            .filter_by(
                session_id_fk=session.id,
                namespace=namespace,
                memory_key=memory_key,
            )
            .first()
        )

        if record:
            record.memory_value_json = json.dumps(value, ensure_ascii=False)
            record.updated_at = datetime.utcnow()
        else:
            record = LongTermMemoryRecord(
                session_id_fk=session.id,
                namespace=namespace,
                memory_key=memory_key,
                memory_value_json=json.dumps(value, ensure_ascii=False),
            )
            db.add(record)

        db.commit()
        db.refresh(record)
        return record

    def get_memory(
        self,
        db: Session,
        session_id: str,
        namespace: str,
        memory_key: str,
    ) -> dict | None:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            return None

        record = (
            db.query(LongTermMemoryRecord)
            .filter_by(
                session_id_fk=session.id,
                namespace=namespace,
                memory_key=memory_key,
            )
            .first()
        )

        if not record:
            return None

        return json.loads(record.memory_value_json)

    def list_memories(
        self,
        db: Session,
        session_id: str,
        namespace: str,
    ) -> list[dict]:
        session = db.query(ChatSession).filter_by(session_id=session_id).first()
        if not session:
            return []

        records = (
            db.query(LongTermMemoryRecord)
            .filter_by(
                session_id_fk=session.id,
                namespace=namespace,
            )
            .all()
        )

        return [
            {
                "memory_key": record.memory_key,
                "value": json.loads(record.memory_value_json),
            }
            for record in records
        ]