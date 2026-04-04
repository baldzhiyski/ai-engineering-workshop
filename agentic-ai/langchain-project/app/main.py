from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool
import logging
from contextlib import asynccontextmanager

from .api.routes_rag import  router as rag_router
from .api.routes_chat import router as chat_router
from .api.routes_memory import router as memory_router
from .api.routes_documents import router as documents_router
from .db.init_db import init_db


# Basic logging configuration for the app. This ensures graph node logs (INFO/ERROR)
# are visible on the console when running the app with uvicorn.
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(name)s] %(message)s')


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # init_db is synchronous (SQLAlchemy); run it in a thread to avoid blocking the event loop
        await run_in_threadpool(lambda: init_db())
        logging.getLogger(__name__).info("Database initialized successfully")
        yield
    except Exception:
        logging.getLogger(__name__).exception("Failed to initialize the database on startup")
        raise

app = FastAPI(title="LangChain Agentic Platform", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "LangChain Agentic Platform is running"}


app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(documents_router)
app.include_router(rag_router)