# app/bootstrap.py
from .config import settings
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from .graph.app_graph import build_app_graph

from pathlib import Path

def save_graph_png(graph, filename: str = "app_graph.png", xray: bool = False) -> Path | None:
    out_path = Path(__file__).resolve().parent / filename

    try:
        png_bytes = graph.get_graph(xray=xray).draw_mermaid_png()
        out_path.write_bytes(png_bytes)
        return out_path
    except Exception as e:
        print(f"Graph PNG export skipped: {e}")
        return None


def build_runtime():
    store_cm = PostgresStore.from_conn_string(settings.db_uri)
    checkpointer_cm = PostgresSaver.from_conn_string(settings.db_uri)

    store = store_cm.__enter__()
    checkpointer = checkpointer_cm.__enter__()

    try:
        store.setup()
    except Exception:
        pass

    try:
        checkpointer.setup()
    except Exception:
        pass

    graph = build_app_graph(store=store, checkpointer=checkpointer)
    saved_to = save_graph_png(graph)
    print(f"Graph saved to: {saved_to}")

    return graph, store, checkpointer, store_cm, checkpointer_cm