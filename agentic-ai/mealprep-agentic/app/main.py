# app/api/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from pydantic import BaseModel
from langgraph.types import Command

from .context import AppContext
from .graph.app_graph import  build_app_graph
from .bootstrap import save_graph_png
from .config import settings


class PlanRequest(BaseModel):
    thread_id: str
    user_id: str
    message: str

class ResumeRequest(BaseModel):
    thread_id: str
    user_id: str
    answers: dict

GRAPH = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global GRAPH

    with PostgresStore.from_conn_string(settings.db_uri) as store, \
         PostgresSaver.from_conn_string(settings.db_uri) as checkpointer:

        try:
            store.setup()
        except Exception:
            pass

        try:
            checkpointer.setup()
        except Exception:
            pass

        GRAPH = build_app_graph(store=store, checkpointer=checkpointer)
        saved_to = save_graph_png(GRAPH)
        print(f"Graph saved to: {saved_to}")

        yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "MealPrep Agentic API is running",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/plan")
def plan(req: PlanRequest):
    result = GRAPH.invoke(
        {"messages": [HumanMessage(content=req.message)]},
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
        {"messages":  [HumanMessage(content=req.message)]},
        config={"configurable": {"thread_id": req.thread_id}},
        context=AppContext(user_id=req.user_id),
        stream_mode="updates",
    ):
        events.append(chunk)

    return {"events": events}