# app/tools/safety_tools.py
from __future__ import annotations
from langchain.tools import tool

HIGH_RISK_MEDICATION_HINTS = {"warfarin", "isotretinoin", "insulin"}
SUPPLEMENT_RISK_MAP = {
    "vitamin_k": {"contra": ["warfarin"], "risk": "possible interaction"},
    "iron": {"contra": [], "risk": "avoid unless deficiency or clinician guidance"},
    "magnesium": {"contra": [], "risk": "monitor GI tolerance"},
    "creatine": {"contra": [], "risk": "avoid strong claims; hydration note only"},
}

@tool
def supplement_risk_check(supplements: list[str], medications: list[str]) -> dict:
    """Check supplement suggestions against a curated rule set."""
    flags = []
    meds = {m.lower() for m in medications}
    for supp in supplements:
        rule = SUPPLEMENT_RISK_MAP.get(supp.lower())
        if not rule:
            flags.append(f"Unknown supplement rule for {supp}")
            continue
        for contra in rule["contra"]:
            if contra in meds:
                flags.append(f"{supp} may conflict with {contra}")
    if any(m in HIGH_RISK_MEDICATION_HINTS for m in meds):
        flags.append("Medical review recommended before supplement advice")
    return {"safe": len(flags) == 0, "flags": flags}