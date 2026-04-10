# app/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.types import Command

from .context import AppContext
from .bootstrap import build_runtime

app = FastAPI()

GRAPH, STORE, CHECKPOINTER = build_runtime()

class PlanRequest(BaseModel):
    thread_id: str
    user_id: str
    message: str

class ResumeRequest(BaseModel):
    thread_id: str
    user_id: str
    answers: dict

@app.post("/plan")
def plan(req: PlanRequest):
    result = GRAPH.invoke(
        {"messages": [{"role": "user", "content": req.message}]},
        config={"configurable": {"thread_id": req.thread_id}},
        context=AppContext(user_id=req.user_id),
    )

    if "__interrupt__" in result:
        return {
            "status": "input_required",
            "interrupt": result["__interrupt__"],
        }

    return {
        "status": "completed",
        "result": result,
    }

@app.post("/plan/resume")
def resume_plan(req: ResumeRequest):
    result = GRAPH.invoke(
        Command(resume=req.answers),
        config={"configurable": {"thread_id": req.thread_id}},
        context=AppContext(user_id=req.user_id),
    )

    if "__interrupt__" in result:
        return {
            "status": "input_required",
            "interrupt": result["__interrupt__"],
        }

    return {
        "status": "completed",
        "result": result,
    }

@app.post("/plan/stream")
def stream_plan(req: PlanRequest):
    events = []

    for chunk in GRAPH.stream(
        {"messages": [{"role": "user", "content": req.message}]},
        config={"configurable": {"thread_id": req.thread_id}},
        context=AppContext(user_id=req.user_id),
        stream_mode="updates",
    ):
        events.append(chunk)

    return {"events": events}