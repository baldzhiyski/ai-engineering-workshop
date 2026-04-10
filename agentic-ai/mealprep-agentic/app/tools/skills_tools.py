# app/tools/skills_tool.py
from __future__ import annotations
from pathlib import Path
from langchain.tools import tool

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"

@tool
def load_skill(skill_name: str) -> str:
    """Load a higher-level skill prompt on demand."""
    path = SKILLS_DIR / f"{skill_name}.md"
    if not path.exists():
        return f"Skill {skill_name} not found."
    return path.read_text(encoding="utf-8")