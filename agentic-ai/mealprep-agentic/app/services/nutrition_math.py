# app/services/nutrition_math.py
from __future__ import annotations
from ..domain.models import UserProfile, MacroTargets

def estimate_bmr(profile: UserProfile) -> float:
    # Mifflin-St Jeor-ish baseline
    base = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age
    if profile.sex == "male":
        base += 5
    elif profile.sex == "female":
        base -= 161
    return base

def activity_multiplier(level: str) -> float:
    return {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "high": 1.725,
        "athlete": 1.9,
    }[level]

def compute_macro_targets(profile: UserProfile) -> MacroTargets:
    calories = estimate_bmr(profile) * activity_multiplier(profile.activity_level)

    if profile.goal == "fat_loss":
        calories -= 400
        protein_per_kg = 2.1
        fat_ratio = 0.28
    elif profile.goal == "muscle_gain":
        calories += 250
        protein_per_kg = 2.0
        fat_ratio = 0.25
    elif profile.goal == "athletic_performance":
        calories += 100
        protein_per_kg = 1.8
        fat_ratio = 0.22
    else:
        protein_per_kg = 1.8
        fat_ratio = 0.27

    protein_g = round(profile.weight_kg * protein_per_kg)
    fats_g = round((calories * fat_ratio) / 9)
    carbs_g = round((calories - protein_g * 4 - fats_g * 9) / 4)

    return MacroTargets(
        calories=round(calories),
        protein_g=protein_g,
        carbs_g=max(carbs_g, 0),
        fats_g=fats_g,
    )