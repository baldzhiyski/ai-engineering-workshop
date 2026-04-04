from pathlib import Path
from langchain_core.tools import tool

@tool
def read_text_file(path: str) -> str:
    """Read a UTF-8 text file from disk."""
    p = Path(path)
    if not p.exists():
        return "file not found"
    return p.read_text(encoding="utf-8")