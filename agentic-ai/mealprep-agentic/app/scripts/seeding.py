
from langgraph.store.postgres import PostgresStore
from ..config import settings

RECIPES = [
    {
        "name": "Greek Yogurt Oats",
        "tags": ["high_protein", "breakfast"],
        "calories": 450,
        "protein_g": 35,
        "carbs_g": 45,
        "fats_g": 12,
    },
    {
        "name": "Chicken Rice Bowl",
        "tags": ["lunch", "performance"],
        "calories": 700,
        "protein_g": 55,
        "carbs_g": 70,
        "fats_g": 18,
    },
    {
        "name": "Salmon Potato Plate",
        "tags": ["dinner", "omega3"],
        "calories": 760,
        "protein_g": 48,
        "carbs_g": 58,
        "fats_g": 30,
    },
    {
        "name": "Veggie Stir Fry",
        "tags": ["vegan", "low_carb"],
        "calories": 400,
        "protein_g": 15,
        "carbs_g": 30,
        "fats_g": 20,
    },
    {
        "name": "Beef Quinoa Salad",
        "tags": ["high_protein", "lunch"],
        "calories": 650,
        "protein_g": 50,
        "carbs_g": 40,
        "fats_g": 25,
    },
    {
        "name": "Tofu Veggie Bowl",
        "tags": ["vegan", "dinner"],
        "calories": 550,
        "protein_g": 30,
        "carbs_g": 45,
        "fats_g": 15,
    },
    {
        "name": "Egg Avocado Toast",
        "tags": ["breakfast", "vegetarian"],
        "calories": 500,
        "protein_g": 20,
        "carbs_g": 35,
        "fats_g": 25,
    },
    {
        "name": "Turkey Sweet Potato",
        "tags": ["performance", "dinner"],
        "calories": 720,
        "protein_g": 60,
        "carbs_g": 50,
        "fats_g": 20,
    },
    {
        "name": "Quinoa Veggie Salad",
        "tags": ["vegan", "lunch"],
        "calories": 480,
        "protein_g": 18,
        "carbs_g": 55,
        "fats_g": 15,
    },
    {
        "name": "Avocado Chickpea Wrap",
        "tags": ["vegan", "lunch"],
        "calories": 500,
        "protein_g": 20,
        "carbs_g": 50,
        "fats_g": 20,
    },
]

GUIDELINES = [
    {"text": "Prefer protein distribution across meals."},
    {"text": "Keep prep complexity low for adherence."},
    {"text": "Do not overclaim supplement efficacy."},
    {"text": "Flag medication-related supplement advice for human review."},
]

USER_PROFILE = {
    "user_id": "user_123",
    "age": 31,
    "sex": "male",
    "height_cm": 182,
    "weight_kg": 84,
    "activity_level": "high",
    "goal": "athletic_performance",
    "diet_style": ["high_protein"],
    "allergies": ["peanuts"],
    "disliked_foods": ["liver"],
    "medical_flags": [],
    "medications": [],
    "pantry_items": ["oats", "rice", "olive oil"],
    "budget_per_week": 95,
    "meals_per_day": 4,
}

USER_PREFERENCES = [
    {"key": "response_style", "value": "concise"},
    {"key": "meal_prep_style", "value": "repeatable"},
]

USER_PATTERNS = [
    {"key": "successful_breakfast_pattern", "value": "high_protein_oats"},
    {"key": "preferred_lunch_pattern", "value": "rice_bowl"},
]

SUPPLEMENT_RISK_RULES = {
    "vitamin_k": {
        "contra": ["warfarin"],
        "risk": "possible interaction",
    },
    "iron": {
        "contra": [],
        "risk": "avoid unless deficiency or clinician guidance",
    },
    "magnesium": {
        "contra": [],
        "risk": "monitor GI tolerance",
    },
    "creatine": {
        "contra": [],
        "risk": "avoid strong claims; hydration note only",
    },
}

HIGH_RISK_MEDICATIONS = {
    "warfarin": {
        "reason": "high interaction potential with nutrition/supplement advice"
    },
    "isotretinoin": {
        "reason": "requires caution with supplement and vitamin advice"
    },
    "insulin": {
        "reason": "dietary changes may affect glucose management"
    },
}



def main() -> None:
    with PostgresStore.from_conn_string(settings.db_uri) as store:
        store.setup()
        # Seed supplement rules
        for supplement_name, rule in SUPPLEMENT_RISK_RULES.items():
            store.put(
                ("domain", "safety", "supplement_rules"),
                supplement_name,
                {
                    "name": supplement_name,
                    "contra": rule["contra"],
                    "risk": rule["risk"],
                },
            )

        # Seed high-risk medications
        for med_name, rule in HIGH_RISK_MEDICATIONS.items():
            store.put(
                ("domain", "safety", "high_risk_medications"),
                med_name,
                {
                    "name": med_name,
                    "reason": rule["reason"],
                },
            )

        # user profile
        store.put(("users", "user_123", "profile"), "current", USER_PROFILE)

        # preferences
        for item in USER_PREFERENCES:
            store.put(("users", "user_123", "preferences"), item["key"], item)

        # patterns
        for item in USER_PATTERNS:
            store.put(("users", "user_123", "patterns"), item["key"], item)

        # recipes
        for i, recipe in enumerate(RECIPES, start=1):
            store.put(("catalog", "recipes"), f"recipe_{i}", recipe)

        # domain guidelines
        for i, doc in enumerate(GUIDELINES, start=1):
            store.put(("domain", "guidelines"), f"guideline_{i}", doc)

        print("Seed completed.")


if __name__ == "__main__":
    main()