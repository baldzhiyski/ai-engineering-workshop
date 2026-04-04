import sqlite3
from langchain_core.tools import tool

DB_PATH = "data/db/app.db"

@tool
def run_sql(query: str) -> str:
    """Execute a read-only SQL query against the local SQLite database."""
    if not query.strip().lower().startswith("select"):
        return "Only SELECT queries are allowed"

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(query).fetchall()
        return str(rows)
    except Exception as exc:
        return f"sql error: {exc}"
    finally:
        conn.close()