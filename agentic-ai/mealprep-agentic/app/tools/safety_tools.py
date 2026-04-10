# app/tools/safety_tools.py
from __future__ import annotations
from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime
from ..context import AppContext


@tool
def supplement_risk_check(
    supplements: list[str],
    medications: list[str],
    runtime: ToolRuntime[AppContext],
) -> dict:
    """Check supplement suggestions against safety rules stored in Postgres."""
    assert runtime.store is not None

    meds = {m.lower().strip() for m in medications if m and m.lower().strip() != "none"}
    flags: list[str] = []

    # Load high-risk medication list from store
    high_risk_docs = runtime.store.search(
        ("domain", "safety", "high_risk_medications"),
        limit=200,
    )
    high_risk_meds = {doc.key.lower() for doc in high_risk_docs}

    for supp in supplements:
        supp_key = supp.lower().strip()

        rule_doc = runtime.store.get(
            ("domain", "safety", "supplement_rules"),
            supp_key,
        )

        if not rule_doc:
            flags.append(f"Unknown supplement rule for {supp}")
            continue

        rule = rule_doc.value
        contraindications = {c.lower() for c in rule.get("contra", [])}

        for contra in contraindications:
            if contra in meds:
                flags.append(f"{supp} may conflict with {contra}")

        risk_note = rule.get("risk")
        if risk_note:
            flags.append(f"{supp}: {risk_note}")

    if any(med in high_risk_meds for med in meds):
        flags.append("Medical review recommended before supplement advice")

    return {
        "safe": len(flags) == 0,
        "flags": flags,
    }