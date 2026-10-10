"""Helpers that build valid domain objects for tests."""
from datetime import date, datetime

from fitness.devices import Device
from fitness.exercises import Exercise, Workout, WorkoutSet
from fitness.users import Account, Subscription, SubscriptionPlan, User, UserProfile

TODAY = date(2026, 10, 10)
NOW = datetime(2026, 10, 10, 9, 0)
PASSWORD = "secret123"


def make_profile(gender: str = "male") -> UserProfile:
    return UserProfile(180.0, 80.0, gender)


def make_user(user_id: int = 1, name: str = "Alex") -> User:
    account = Account.create(f"{name.lower()}@mail.com", PASSWORD, NOW)
    return User(user_id, name, f"{name.lower()}@mail.com", date(1995, 5, 20), account, make_profile())


def make_plan(coaching: bool = True) -> SubscriptionPlan:
    return SubscriptionPlan("Pro", 9.99, coaching, 3)


def make_subscription(coaching: bool = True) -> Subscription:
    return Subscription(make_plan(coaching), date(2026, 10, 1), date(2026, 10, 31))


def make_device(user: User | None = None, connected: bool = True) -> Device:
    device = Device(1, "FitBand", user or make_user())
    if connected:
        device.connect()
    return device


def make_exercise(name: str = "Bench press", group: str = "chest") -> Exercise:
    return Exercise(name, group, 6.0, 3)


def make_set(reps: int = 10, weight: float = 50.0, name: str = "Bench press") -> WorkoutSet:
    return WorkoutSet(make_exercise(name), reps, weight, 60)


def make_workout(workout_id: int = 1, day: date = TODAY) -> Workout:
    workout = Workout(workout_id, "Push day", day, 45)
    workout.add_set(make_set())
    workout.add_set(make_set(8, 60.0))
    return workout
