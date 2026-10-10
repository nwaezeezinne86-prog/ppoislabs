"""Exercises, workouts, plans and live sessions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING

from .constants import (
    EPLEY_DIVISOR, MAX_DIFFICULTY, MIN_DIFFICULTY, MIN_REPS, MUSCLE_GROUPS, SECONDS_PER_MINUTE, SECONDS_PER_REP,
)
from .exceptions import InvalidWorkoutException, WorkoutNotFoundException

if TYPE_CHECKING:
    from .coaching import Trainer
    from .health import HeartRateMonitor
    from .users import User


@dataclass
class Exercise:
    """A named movement that trains a muscle group."""

    name: str
    muscle_group: str
    calories_per_minute: float
    difficulty: int

    def validate(self) -> None:
        if self.muscle_group not in MUSCLE_GROUPS:
            raise InvalidWorkoutException(f"Unknown muscle group: {self.muscle_group}")
        if self.calories_per_minute <= 0:
            raise InvalidWorkoutException("Calories per minute must be positive")
        if not MIN_DIFFICULTY <= self.difficulty <= MAX_DIFFICULTY:
            raise InvalidWorkoutException("Difficulty out of range")

    def calories_burned(self, minutes: float) -> float:
        return self.calories_per_minute * minutes

    def targets(self, muscle_group: str) -> bool:
        return self.muscle_group in (muscle_group, "full body")


@dataclass
class WorkoutSet:
    """Repetitions of one exercise with a load."""

    exercise: Exercise
    reps: int
    weight_kg: float
    rest_seconds: int

    def validate(self) -> None:
        if self.reps < MIN_REPS or self.weight_kg < 0 or self.rest_seconds < 0:
            raise InvalidWorkoutException("Set values must be non-negative and reps positive")

    def volume(self) -> float:
        return self.reps * self.weight_kg

    def estimated_one_rep_max(self) -> float:
        return self.weight_kg * (1 + self.reps / EPLEY_DIVISOR)

    def duration_seconds(self) -> int:
        return self.reps * SECONDS_PER_REP + self.rest_seconds


@dataclass
class Workout:
    """A strength workout made of sets."""

    workout_id: int
    name: str
    performed_on: date
    duration_minutes: int
    sets: list[WorkoutSet] = field(default_factory=list)

    def validate(self) -> None:
        if not self.sets or self.duration_minutes <= 0:
            raise InvalidWorkoutException("Workout needs sets and a positive duration")

    def add_set(self, workout_set: WorkoutSet) -> None:
        workout_set.validate()
        self.sets.append(workout_set)

    def total_volume(self) -> float:
        return sum(item.volume() for item in self.sets)

    def calories_burned(self) -> float:
        return sum(item.exercise.calories_burned(item.duration_seconds() / SECONDS_PER_MINUTE) for item in self.sets)

    def muscle_groups(self) -> set[str]:
        return {item.exercise.muscle_group for item in self.sets}

    def exercise_count(self) -> int:
        return len({item.exercise.name for item in self.sets})


@dataclass
class WorkoutPlan:
    """A multi-week programme of workouts."""

    name: str
    weeks: int
    workouts: list[Workout] = field(default_factory=list)
    author: Trainer | None = None

    def add_workout(self, workout: Workout) -> None:
        workout.validate()
        self.workouts.append(workout)

    def find_workout(self, name: str) -> Workout:
        for workout in self.workouts:
            if workout.name == name:
                return workout
        raise WorkoutNotFoundException(f"Workout not found: {name}")

    def total_sessions(self) -> int:
        return len(self.workouts) * self.weeks

    def average_duration(self) -> float:
        if not self.workouts:
            return 0.0
        return sum(item.duration_minutes for item in self.workouts) / len(self.workouts)


@dataclass
class WorkoutSession:
    """A live execution of a workout by a user."""

    workout: Workout
    user: User
    started_at: datetime | None = None
    finished_at: datetime | None = None
    monitor: HeartRateMonitor | None = None

    def begin(self, now: datetime) -> None:
        if self.started_at is not None:
            raise InvalidWorkoutException("Session already started")
        self.started_at = now

    def finish(self, now: datetime) -> None:
        if self.started_at is None or now < self.started_at:
            raise InvalidWorkoutException("Session cannot finish before it starts")
        self.finished_at = now

    def is_finished(self) -> bool:
        return self.finished_at is not None

    def elapsed_minutes(self) -> float:
        if self.started_at is None or self.finished_at is None:
            return 0.0
        return (self.finished_at - self.started_at).total_seconds() / SECONDS_PER_MINUTE

    def average_heart_rate(self) -> float:
        return self.monitor.average_bpm() if self.monitor else 0.0
