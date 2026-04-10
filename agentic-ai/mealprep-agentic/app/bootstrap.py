# app/bootstrap.py
from .config import settings
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from .graph.app_graph import build_app_graph

from pathlib import Path

def save_graph_png(graph, filename: str = "app_graph.png", xray: bool = True) -> Path:
    # Save next to this Python file
    out_path = Path(__file__).resolve().parent / filename

    png_bytes = graph.get_graph(xray=xray).draw_mermaid_png()
    out_path.write_bytes(png_bytes)

    return out_path


def build_runtime():
    store = PostgresStore.from_conn_string(settings.db_uri)
    checkpointer = PostgresSaver.from_conn_string(settings.db_uri)

    store.__enter__()
    checkpointer.__enter__()

    # setup once / safe to call at startup
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
    return graph, store, checkpointer