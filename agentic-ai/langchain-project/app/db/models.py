from datetime import datetime
from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.session import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(String(128), default="default-user")
    title: Mapped[str] = mapped_column(String(255), default="Untitled Session")
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    workflow_runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["DocumentRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    memories: Mapped[list["LongTermMemoryRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id_fk: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String(50), default="chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id_fk: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    task_type: Mapped[str] = mapped_column(String(100), default="general")
    status: Mapped[str] = mapped_column(String(50), default="running")
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["ChatSession"] = relationship(back_populates="workflow_runs")
    checkpoints: Mapped[list["WorkflowCheckpoint"]] = relationship(
        back_populates="workflow_run",
        cascade="all, delete-orphan",
    )


class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_run_id_fk: Mapped[int] = mapped_column(ForeignKey("workflow_runs.id"))
    step_name: Mapped[str] = mapped_column(String(100))
    state_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workflow_run: Mapped["WorkflowRun"] = relationship(back_populates="checkpoints")


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id_fk: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100), default="unknown")
    ingestion_status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="documents")


class LongTermMemoryRecord(Base):
    __tablename__ = "long_term_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id_fk: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    namespace: Mapped[str] = mapped_column(String(255), default="default")
    memory_key: Mapped[str] = mapped_column(String(255))
    memory_value_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped["ChatSession"] = relationship(back_populates="memories")