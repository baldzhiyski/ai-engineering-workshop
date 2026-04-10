from __future__ import annotations
from langchain.tools import tool, ToolRuntime
from ..context import AppContext
from ..domain.models import UserProfile
from ..services.nutrition_math import compute_macro_targets


@tool
def calculate_macro_targets(profile_json : dict,runtime : ToolRuntime[AppContext]) -> dict:
    """Calculate calorie and macro targets deterministically."""
    profile = UserProfile.model_validate(profile_json)
    return compute_macro_targets(profile).model_dump()

@tool
def analyze_meal_totals(meals: list[dict]) -> dict:
    """Sum calories and macros over generated meals."""
    total = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fats_g": 0}
    for meal in meals:
        total["calories"] += meal.get("calories", 0)
        total["protein_g"] += meal.get("protein_g", 0)
        total["carbs_g"] += meal.get("carbs_g", 0)
        total["fats_g"] += meal.get("fats_g", 0)
    return total

