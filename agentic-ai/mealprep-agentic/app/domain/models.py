# app/domain/models.py
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal

Goal = Literal["fat_loss", "maintenance", "muscle_gain", "athletic_performance"]
Sex = Literal["male", "female", "other"]

class UserProfile(BaseModel):
    user_id: str
    age: int
    sex: Sex
    height_cm: float
    weight_kg: float
    activity_level: Literal["sedentary", "light", "moderate", "high", "athlete"]
    goal: Goal
    diet_style: list[str] = Field(default_factory=list)   # e.g. vegetarian, halal
    allergies: list[str] = Field(default_factory=list)
    disliked_foods: list[str] = Field(default_factory=list)
    medical_flags: list[str] = Field(default_factory=list)   # not diagnoses, operational flags
    medications: list[str] = Field(default_factory=list)
    pantry_items: list[str] = Field(default_factory=list)
    budget_per_week: float | None = None
    meals_per_day: int = 3

class MacroTargets(BaseModel):
    calories: int
    protein_g: int
    carbs_g: int
    fats_g: int

class Meal(BaseModel):
    name: str
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    ingredients: list[str]
    instructions: list[str]
    calories: int
    protein_g: int
    carbs_g: int
    fats_g: int

class DayPlan(BaseModel):
    day: str
    meals: list[Meal]
    totals: MacroTargets

class SupplementRecommendation(BaseModel):
    name: str
    reason: str
    dosage_note: str
    caution: str

class GroceryItem(BaseModel):
    item: str
    quantity: str
    estimated_cost: float | None = None

class MealPlan(BaseModel):
    summary: str
    target_macros: MacroTargets
    week: list[DayPlan]
    grocery_list: list[GroceryItem]
    supplements: list[SupplementRecommendation] = Field(default_factory=list)
    adherence_tips: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class ValidationReport(BaseModel):
    approved: bool
    issues: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)