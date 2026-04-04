from fastapi import APIRouter
from pydantic import BaseModel

from ..rag.ingest import ingest_file
from ..rag.qa_chain import ask_rag

router = APIRouter(prefix="/rag", tags=["rag"])


class IngestRequest(BaseModel):
    path: str


class AskRequest(BaseModel):
    question: str
    k: int = 5


@router.post("/ingest")
def ingest(req: IngestRequest):
    return ingest_file(req.path)


@router.post("/ask")
def ask(req: AskRequest):
    return ask_rag(req.question, k=req.k)