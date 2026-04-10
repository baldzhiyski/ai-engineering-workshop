from __future__ import annotations
from langchain.tools import tool, ToolRuntime
from ..context import AppContext
from ..config import settings


@tool
def search_recipe_corpus(
    query: str,
    meal_type: str | None = None,
    runtime: ToolRuntime[AppContext] = None,
) -> list[dict]:
    """Search recipe catalog stored in Postgres-backed store."""
    if runtime is None or runtime.store is None:
        raise ValueError("Recipe search requires runtime.store")

    docs = runtime.store.search(("catalog", "recipes"), limit=200)

    results: list[dict] = []
    q = query.lower().strip()

    for doc in docs:
        item = doc.value
        name = item.get("name", "")
        tags = item.get("tags", [])
        hay = f"{name} {' '.join(tags)}".lower()

        if q in hay or any(tok in hay for tok in q.split()):
            if meal_type is None or meal_type in tags:
                results.append(item)

    return results[: settings.max_recipe_results]