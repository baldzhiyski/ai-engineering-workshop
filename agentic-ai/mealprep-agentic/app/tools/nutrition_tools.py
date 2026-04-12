from __future__ import annotations
from langchain.tools import tool, ToolRuntime
from pydantic import Field, BaseModel

from ..context import AppContext
from ..domain.models import UserProfile
from ..services.nutrition_math import compute_macro_targets


@tool(args_schema=UserProfile)
def calculate_macro_targets(profile_json : UserProfile,runtime : ToolRuntime[AppContext]) -> dict:
    """Calculate calorie and macro targets deterministically."""
    profile = UserProfile.model_validate(profile_json)
    return compute_macro_targets(profile).model_dump()


class MealTotalsEntry(BaseModel):
    calories: int = Field(description="Calories in the meal")
    protein_g: int = Field(description="Protein grams in the meal")
    carbs_g: int = Field(description="Carbohydrate grams in the meal")
    fats_g: int = Field(description="Fat grams in the meal")


class MealTotalsInput(BaseModel):
    meals: list[MealTotalsEntry] = Field(
        description="List of meals with only macro totals"
    )


@tool(args_schema=MealTotalsInput)
def analyze_meal_totals(meals: list[MealTotalsEntry]) -> dict:
    """Sum calories and macros over generated meals."""
    total = {
        "calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fats_g": 0,
    }

    for meal in meals:
        total["calories"] += meal.calories
        total["protein_g"] += meal.protein_g
        total["carbs_g"] += meal.carbs_g
        total["fats_g"] += meal.fats_g

    return total

