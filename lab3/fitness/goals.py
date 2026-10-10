"""Goals, badges, streaks and achievements."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import TYPE_CHECKING

from .constants import DAYS_PER_WEEK, PERCENT
from .exceptions import DuplicateEntryException, GoalNotAchievableException

if TYPE_CHECKING:
    from .users import User


@dataclass
class Goal:
    """A measurable target with a deadline."""

    goal_id: int
    title: str
    target_value: float
    deadline: date
    owner: User
    current_value: float = 0.0

    def validate(self, today: date) -> None:
        if self.target_value <= 0:
            raise GoalNotAchievableException("Target must be positive")
        if self.deadline < today:
            raise GoalNotAchievableException("Deadline is in the past")

    def progress_percent(self) -> float:
        return min(self.current_value / self.target_value * PERCENT, PERCENT)

    def is_achieved(self) -> bool:
        return self.current_value >= self.target_value

    def update_progress(self, value: float) -> None:
        self.current_value = value

    def days_remaining(self, today: date) -> int:
        return (self.deadline - today).days

    def is_overdue(self, today: date) -> bool:
        return today > self.deadline and not self.is_achieved()


@dataclass
class WeightGoal(Goal):
    """Reach a target body weight."""

    start_weight_kg: float = 0.0

    def validate(self, today: date) -> None:
        super().validate(today)
        if self.start_weight_kg == self.target_value:
            raise GoalNotAchievableException("Start weight equals target weight")

    def progress_percent(self) -> float:
        total_change = self.start_weight_kg - self.target_value
        done_change = self.start_weight_kg - self.current_value
        return max(min(done_change / total_change * PERCENT, PERCENT), 0.0)

    def is_achieved(self) -> bool:
        if self.start_weight_kg > self.target_value:
            return self.current_value <= self.target_value
        return self.current_value >= self.target_value

    def required_weekly_change(self, today: date) -> float:
        days_left = self.days_remaining(today)
        if days_left <= 0:
            raise GoalNotAchievableException("No time left to reach the goal")
        return (self.target_value - self.current_value) / (days_left / DAYS_PER_WEEK)


@dataclass
class DistanceGoal(Goal):
    """Cover a total distance in kilometres."""

    def add_distance(self, kilometres: float) -> None:
        if kilometres < 0:
            raise GoalNotAchievableException("Distance cannot be negative")
        self.current_value += kilometres

    def remaining_km(self) -> float:
        return max(self.target_value - self.current_value, 0.0)


@dataclass
class WorkoutFrequencyGoal(Goal):
    """Train a number of times per week."""

    sessions_per_week: int = 0

    def register_workout(self) -> None:
        self.current_value += 1

    def is_on_track(self, weeks_elapsed: int) -> bool:
        return self.current_value >= self.sessions_per_week * weeks_elapsed


@dataclass
class Badge:
    """A reward for an achievement."""

    name: str
    description: str
    points: int
    earned_on: date | None = None

    def award(self, day: date) -> None:
        if self.earned_on is not None:
            raise DuplicateEntryException(f"Badge already earned: {self.name}")
        self.earned_on = day

    def is_earned(self) -> bool:
        return self.earned_on is not None


@dataclass
class Streak:
    """Consecutive days with activity."""

    current_days: int = 0
    longest_days: int = 0
    last_active: date | None = None

    def record_activity(self, day: date) -> None:
        if self.last_active == day:
            return
        if self.last_active is not None and day == self.last_active + timedelta(days=1):
            self.current_days += 1
        else:
            self.current_days = 1
        self.longest_days = max(self.longest_days, self.current_days)
        self.last_active = day

    def is_active(self, today: date) -> bool:
        if self.last_active is None:
            return False
        return (today - self.last_active).days <= 1

    def reset(self) -> None:
        self.current_days = 0
        self.last_active = None


@dataclass
class AchievementManager:
    """Keeps goals, badges and the streak of one user."""

    user: User
    goals: list[Goal] = field(default_factory=list)
    badges: list[Badge] = field(default_factory=list)
    streak: Streak = field(default_factory=Streak)

    def add_goal(self, goal: Goal, today: date) -> None:
        goal.validate(today)
        self.goals.append(goal)

    def award_badge(self, badge: Badge, day: date) -> None:
        badge.award(day)
        self.badges.append(badge)

    def total_points(self) -> int:
        return sum(item.points for item in self.badges)

    def achieved_goals(self) -> list[Goal]:
        return [goal for goal in self.goals if goal.is_achieved()]

    def overdue_goals(self, today: date) -> list[Goal]:
        return [goal for goal in self.goals if goal.is_overdue(today)]
