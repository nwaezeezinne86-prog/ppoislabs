"""Foods, meals, recipes, meal plans and nutrition logs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING

from .constants import (
    KCAL_PER_GRAM_CARBS, KCAL_PER_GRAM_FAT, KCAL_PER_GRAM_PROTEIN, MEAL_TYPES, PERCENT,
)
from .exceptions import InvalidNutritionDataException

if TYPE_CHECKING:
    from .users import User


@dataclass
class Food:
    """A food item with macronutrients."""

    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

    def validate(self) -> None:
        values = (self.calories, self.protein_g, self.carbs_g, self.fat_g)
        if any(value < 0 for value in values):
            raise InvalidNutritionDataException(f"Negative nutrition value in {self.name}")

    def macro_calories(self) -> float:
        return (self.protein_g * KCAL_PER_GRAM_PROTEIN + self.carbs_g * KCAL_PER_GRAM_CARBS
                + self.fat_g * KCAL_PER_GRAM_FAT)

    def scaled(self, factor: float) -> Food:
        if factor <= 0:
            raise InvalidNutritionDataException("Portion factor must be positive")
        return Food(self.name, self.calories * factor, self.protein_g * factor,
                    self.carbs_g * factor, self.fat_g * factor)


@dataclass
class Meal:
    """Foods eaten together."""

    meal_type: str
    eaten_at: datetime
    foods: list[Food] = field(default_factory=list)

    def validate(self) -> None:
        if self.meal_type not in MEAL_TYPES:
            raise InvalidNutritionDataException(f"Unknown meal type: {self.meal_type}")

    def add_food(self, food: Food) -> None:
        food.validate()
        self.foods.append(food)

    def total_calories(self) -> float:
        return sum(item.calories for item in self.foods)

    def total_protein(self) -> float:
        return sum(item.protein_g for item in self.foods)

    def macro_split(self) -> dict[str, float]:
        total = sum(item.macro_calories() for item in self.foods)
        if total == 0:
            return {"protein": 0.0, "carbs": 0.0, "fat": 0.0}
        protein = sum(item.protein_g for item in self.foods) * KCAL_PER_GRAM_PROTEIN
        carbs = sum(item.carbs_g for item in self.foods) * KCAL_PER_GRAM_CARBS
        fat = sum(item.fat_g for item in self.foods) * KCAL_PER_GRAM_FAT
        return {name: value / total * PERCENT for name, value in
                (("protein", protein), ("carbs", carbs), ("fat", fat))}


@dataclass
class Recipe:
    """A dish assembled from ingredients."""

    title: str
    servings: int
    ingredients: list[Food] = field(default_factory=list)
    author: User | None = None

    def add_ingredient(self, food: Food) -> None:
        food.validate()
        self.ingredients.append(food)

    def total_calories(self) -> float:
        return sum(item.calories for item in self.ingredients)

    def calories_per_serving(self) -> float:
        if self.servings <= 0:
            raise InvalidNutritionDataException("Servings must be positive")
        return self.total_calories() / self.servings

    def to_meal(self, meal_type: str, eaten_at: datetime) -> Meal:
        meal = Meal(meal_type, eaten_at)
        meal.validate()
        meal.add_food(Food(self.title, self.calories_per_serving(), 0.0, 0.0, 0.0))
        return meal


@dataclass
class MealPlan:
    """Planned meals for a day against a calorie target."""

    owner: User
    daily_calorie_target: float
    meals: list[Meal] = field(default_factory=list)

    def add_meal(self, meal: Meal) -> None:
        meal.validate()
        self.meals.append(meal)

    def planned_calories(self) -> float:
        return sum(item.total_calories() for item in self.meals)

    def remaining_calories(self) -> float:
        return self.daily_calorie_target - self.planned_calories()

    def is_within_target(self) -> bool:
        return self.planned_calories() <= self.daily_calorie_target


@dataclass
class NutritionLog:
    """History of eaten meals for one user."""

    user: User
    meals: list[Meal] = field(default_factory=list)

    def log_meal(self, meal: Meal) -> None:
        meal.validate()
        self.meals.append(meal)

    def calories_on(self, day: date) -> float:
        return sum(item.total_calories() for item in self.meals if item.eaten_at.date() == day)

    def protein_on(self, day: date) -> float:
        return sum(item.total_protein() for item in self.meals if item.eaten_at.date() == day)

    def average_daily_calories(self) -> float:
        days = {item.eaten_at.date() for item in self.meals}
        if not days:
            return 0.0
        return sum(item.total_calories() for item in self.meals) / len(days)
