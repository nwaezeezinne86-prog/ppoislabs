"""Calculators and progress analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from .constants import (
    BMI_NORMAL_LIMIT, BMI_OVERWEIGHT_LIMIT, BMI_UNDERWEIGHT_LIMIT, BMR_AGE_COEFFICIENT, BMR_FEMALE_OFFSET,
    BMR_HEIGHT_COEFFICIENT, BMR_MALE_OFFSET, BMR_WEIGHT_COEFFICIENT, DAYS_PER_WEEK, KCAL_PER_KG_FAT, PERCENT,
    TREND_THRESHOLD_PERCENT,
)
from .exceptions import InvalidMeasurementException, InvalidWorkoutException

if TYPE_CHECKING:
    from .activities import CardioActivity
    from .exercises import Exercise, Workout
    from .goals import WeightGoal
    from .users import User, UserProfile


@dataclass
class BMICalculator:
    """Body mass index calculations."""

    precision: int = 1

    def calculate(self, weight_kg: float, height_m: float) -> float:
        if height_m <= 0:
            raise InvalidMeasurementException("Height must be positive")
        return round(weight_kg / height_m ** 2, self.precision)

    def category(self, bmi: float) -> str:
        if bmi < BMI_UNDERWEIGHT_LIMIT:
            return "underweight"
        if bmi < BMI_NORMAL_LIMIT:
            return "normal"
        return "overweight" if bmi < BMI_OVERWEIGHT_LIMIT else "obese"

    def classify(self, profile: UserProfile) -> str:
        return self.category(self.calculate(profile.weight_kg, profile.height_m()))


@dataclass
class CalorieCalculator:
    """Energy expenditure calculations."""

    rounding_digits: int = 0

    def basal_rate(self, profile: UserProfile, age: int) -> float:
        offset = BMR_MALE_OFFSET if profile.gender == "male" else BMR_FEMALE_OFFSET
        rate = (BMR_WEIGHT_COEFFICIENT * profile.weight_kg + BMR_HEIGHT_COEFFICIENT * profile.height_cm
                - BMR_AGE_COEFFICIENT * age + offset)
        return round(rate, self.rounding_digits)

    def daily_needs(self, profile: UserProfile, age: int) -> float:
        return round(self.basal_rate(profile, age) * profile.activity_multiplier(), self.rounding_digits)

    def calories_for_weight_change(self, kilograms: float) -> float:
        return kilograms * KCAL_PER_KG_FAT

    def daily_adjustment(self, goal: WeightGoal, today: date) -> float:
        weekly_kg = goal.required_weekly_change(today)
        return self.calories_for_weight_change(weekly_kg) / DAYS_PER_WEEK


@dataclass
class ProgressReport:
    """Summary of a user's activity over a period."""

    user: User
    period_start: date
    period_end: date
    workouts: list[Workout] = field(default_factory=list)
    activities: list[CardioActivity] = field(default_factory=list)

    def total_workouts(self) -> int:
        return len(self.workouts) + len(self.activities)

    def total_calories(self) -> float:
        strength = sum(item.calories_burned() for item in self.workouts)
        cardio = sum(item.calories_burned() for item in self.activities)
        return strength + cardio

    def total_volume(self) -> float:
        return sum(item.total_volume() for item in self.workouts)

    def total_distance_km(self) -> float:
        return sum(item.distance_km for item in self.activities)

    def average_workout_minutes(self) -> float:
        if not self.workouts:
            return 0.0
        return sum(item.duration_minutes for item in self.workouts) / len(self.workouts)


@dataclass
class ProgressAnalyzer:
    """Compares reports and detects trends."""

    trend_threshold: float = TREND_THRESHOLD_PERCENT

    def compare_volume(self, earlier: ProgressReport, later: ProgressReport) -> float:
        base = earlier.total_volume()
        if base == 0:
            return 0.0
        return (later.total_volume() - base) / base * PERCENT

    def trend(self, values: list[float]) -> str:
        if len(values) < 2 or values[0] == 0:
            return "stable"
        change = (values[-1] - values[0]) / values[0] * PERCENT
        if change > self.trend_threshold:
            return "improving"
        return "declining" if change < -self.trend_threshold else "stable"

    def best_workout(self, workouts: list[Workout]) -> Workout:
        if not workouts:
            raise InvalidWorkoutException("No workouts to compare")
        return max(workouts, key=lambda item: item.total_volume())

    def personal_record(self, workouts: list[Workout], exercise: Exercise) -> float:
        maxima = [item.estimated_one_rep_max() for workout in workouts
                  for item in workout.sets if item.exercise.name == exercise.name]
        return max(maxima, default=0.0)
