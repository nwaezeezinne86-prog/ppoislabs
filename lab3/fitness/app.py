"""Facade that ties the fitness tracker domain together."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from .activities import CardioActivity
from .analytics import ProgressReport
from .devices import NotificationService
from .exceptions import AuthenticationException, DuplicateEntryException, InvalidUserDataException
from .exercises import Workout
from .goals import AchievementManager, Goal
from .nutrition import Meal, NutritionLog
from .social import ActivityFeed, ActivityPost, Challenge, Leaderboard
from .users import Account, User, UserProfile


@dataclass
class FitnessApp:
    """Entry point used by the console interface."""

    users: dict[int, User] = field(default_factory=dict)
    workouts: dict[int, list[Workout]] = field(default_factory=dict)
    activities: dict[int, list[CardioActivity]] = field(default_factory=dict)
    nutrition_logs: dict[int, NutritionLog] = field(default_factory=dict)
    achievements: dict[int, AchievementManager] = field(default_factory=dict)
    challenges: dict[str, Challenge] = field(default_factory=dict)
    notifications: NotificationService = field(default_factory=NotificationService)
    feed: ActivityFeed = field(default_factory=ActivityFeed)
    next_user_id: int = 1

    def register_user(self, name: str, email: str, birth_date: date, password: str,
                      profile: UserProfile, now: datetime) -> User:
        if self.find_by_email(email) is not None:
            raise DuplicateEntryException(f"Email already registered: {email}")
        account = Account.create(email, password, now)
        user = User(self.next_user_id, name, email, birth_date, account, profile)
        user.validate(now.date())
        self._store_user(user)
        return user

    def _store_user(self, user: User) -> None:
        self.users[user.user_id] = user
        self.workouts[user.user_id] = []
        self.activities[user.user_id] = []
        self.nutrition_logs[user.user_id] = NutritionLog(user)
        self.achievements[user.user_id] = AchievementManager(user)
        self.next_user_id += 1

    def find_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    def find_user(self, user_id: int) -> User:
        if user_id not in self.users:
            raise InvalidUserDataException(f"Unknown user id: {user_id}")
        return self.users[user_id]

    def login(self, email: str, password: str) -> User:
        user = self.find_by_email(email)
        if user is None:
            raise AuthenticationException("Invalid login or password")
        user.account.authenticate(password)
        return user

    def log_workout(self, user: User, workout: Workout, now: datetime) -> None:
        workout.validate()
        self.workouts[user.user_id].append(workout)
        self.achievements[user.user_id].streak.record_activity(workout.performed_on)
        self.notifications.send(user, f"Workout logged: {workout.name}", now)

    def log_activity(self, user: User, activity: CardioActivity, now: datetime) -> None:
        activity.validate()
        self.activities[user.user_id].append(activity)
        self.achievements[user.user_id].streak.record_activity(activity.started_at.date())
        self.notifications.send(user, f"Cardio logged: {activity.distance_km:.1f} km", now)

    def log_meal(self, user: User, meal: Meal) -> None:
        self.nutrition_logs[user.user_id].log_meal(meal)

    def add_goal(self, user: User, goal: Goal, today: date) -> None:
        self.achievements[user.user_id].add_goal(goal, today)

    def weekly_report(self, user: User, start: date, end: date) -> ProgressReport:
        workouts = [item for item in self.workouts[user.user_id] if start <= item.performed_on <= end]
        activities = [item for item in self.activities[user.user_id] if start <= item.started_at.date() <= end]
        return ProgressReport(user, start, end, workouts, activities)

    def create_challenge(self, challenge: Challenge) -> None:
        if challenge.name in self.challenges:
            raise DuplicateEntryException(f"Challenge exists: {challenge.name}")
        self.challenges[challenge.name] = challenge

    def get_challenge(self, name: str) -> Challenge:
        if name not in self.challenges:
            raise InvalidUserDataException(f"Unknown challenge: {name}")
        return self.challenges[name]

    def join_challenge(self, name: str, user: User) -> None:
        self.get_challenge(name).join(user)

    def leaderboard(self, name: str) -> Leaderboard:
        return Leaderboard(self.get_challenge(name))

    def share_post(self, user: User, content: str, now: datetime) -> ActivityPost:
        post = ActivityPost(user, content, now)
        self.feed.publish(post)
        return post
