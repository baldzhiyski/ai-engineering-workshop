# app/tools/recipe_tools.py
from __future__ import annotations
from langchain.tools import tool

FAKE_RECIPE_DB = [
    {"name": "Greek Yogurt Oats", "tags": ["high_protein", "breakfast"], "calories": 450, "protein_g": 35, "carbs_g": 45, "fats_g": 12},
    {"name": "Chicken Rice Bowl", "tags": ["lunch", "performance"], "calories": 700, "protein_g": 55, "carbs_g": 70, "fats_g": 18},
    {"name": "Salmon Potato Plate", "tags": ["dinner", "omega3"], "calories": 760, "protein_g": 48, "carbs_g": 58, "fats_g": 30},
    {"name": "Veggie Stir Fry", "tags": ["vegan", "low_carb"], "calories": 400, "protein_g": 15, "carbs_g": 30, "fats_g": 20},
    {"name": "Beef Quinoa Salad", "tags": ["high_protein", "lunch"], "calories": 650, "protein_g": 50, "carbs_g": 40, "fats_g": 25},
    {"name": "Tofu Veggie Bowl", "tags": ["vegan", "dinner"], "calories": 550, "protein_g": 30, "carbs_g": 45, "fats_g": 15},
    {"name": "Egg Avocado Toast", "tags": ["breakfast", "vegetarian"], "calories": 500, "protein_g": 20, "carbs_g": 35, "fats_g": 25},
    {"name": "Turkey Sweet Potato", "tags": ["performance", "dinner"], "calories": 720, "protein_g": 60, "carbs_g": 50, "fats_g": 20},
    {"name": "Quinoa Veggie Salad", "tags": ["vegan", "lunch"], "calories": 480, "protein_g": 18, "carbs_g": 55, "fats_g": 15},
    {"name": "Avocado Chickpea Wrap", "tags": ["vegan", "lunch"], "calories": 500, "protein_g": 20, "carbs_g": 50, "fats_g": 20},
    
]

@tool
def search_recipe_corpus(query: str, meal_type: str | None = None) -> list[dict]:
    """Search recipe corpus for candidate meals."""
    results = []
    q = query.lower()
    for item in FAKE_RECIPE_DB:
        hay = f"{item['name']} {' '.join(item['tags'])}".lower()
        if q in hay or any(tok in hay for tok in q.split()):
            if meal_type is None or meal_type in item["tags"]:
                results.append(item)
    return results[:8]