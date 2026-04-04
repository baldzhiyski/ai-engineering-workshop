from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..memory.long_term import LongTermMemory
from ..memory.summarizer import SessionSummarizer

router = APIRouter(prefix="/memory", tags=["memory"])


class PreferenceRequest(BaseModel):
    session_id: str
    key: str
    value: dict


class SummaryRequest(BaseModel):
    session_id: str


@router.post("/preferences")
def save_preference(req: PreferenceRequest, db: Session = Depends(get_db)):
    memory = LongTermMemory()
    memory.save_user_preference(
        db=db,
        session_id=req.session_id,
        key=req.key,
        value=req.value,
    )
    return {
        "status": "saved",
        "session_id": req.session_id,
        "key": req.key,
    }


@router.get("/preferences/{session_id}/{key}")
def get_preference(session_id: str, key: str, db: Session = Depends(get_db)):
    memory = LongTermMemory()
    value = memory.get_user_preference(
        db=db,
        session_id=session_id,
        key=key,
    )
    return {
        "session_id": session_id,
        "key": key,
        "value": value,
    }


@router.post("/summary")
def summarize_session(req: SummaryRequest, db: Session = Depends(get_db)):
    summarizer = SessionSummarizer()
    summary = summarizer.summarize_session(db, req.session_id)
    return {
        "session_id": req.session_id,
        "summary": summary,
    }