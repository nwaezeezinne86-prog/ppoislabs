"""Personal trainers and training sessions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from .constants import (
    MINUTES_PER_HOUR, PLAN_STATUS_CANCELLED, PLAN_STATUS_COMPLETED, PLAN_STATUS_CONFIRMED, PLAN_STATUS_SCHEDULED,
)
from .exceptions import (
    DuplicateEntryException, InvalidUserDataException, SubscriptionRequiredException, TrainerNotAvailableException,
)

if TYPE_CHECKING:
    from .users import User


@dataclass
class Trainer:
    """A personal trainer with a list of clients."""

    trainer_id: int
    name: str
    specialization: str
    hourly_rate: float
    is_available: bool = True
    clients: list[User] = field(default_factory=list)

    def accept_client(self, user: User) -> None:
        if not self.is_available:
            raise TrainerNotAvailableException(f"{self.name} is not accepting clients")
        if self.has_client(user):
            raise DuplicateEntryException(f"{user.name} is already a client of {self.name}")
        self.clients.append(user)

    def has_client(self, user: User) -> bool:
        return any(client.user_id == user.user_id for client in self.clients)

    def release_client(self, user: User) -> None:
        if not self.has_client(user):
            raise InvalidUserDataException(f"{user.name} is not a client of {self.name}")
        self.clients = [client for client in self.clients if client.user_id != user.user_id]

    def session_cost(self, hours: float) -> float:
        return self.hourly_rate * hours

    def pause(self) -> None:
        self.is_available = False

    def resume(self) -> None:
        self.is_available = True


@dataclass
class TrainingSession:
    """A booked meeting between a trainer and a client."""

    trainer: Trainer
    client: User
    scheduled_at: datetime
    duration_minutes: int
    status: str = PLAN_STATUS_SCHEDULED

    def confirm(self) -> None:
        if not self.trainer.is_available:
            raise TrainerNotAvailableException(f"{self.trainer.name} is not available")
        subscription = self.client.subscription
        if subscription is None or not subscription.plan.allows_coaching():
            raise SubscriptionRequiredException("Coaching requires a plan with a trainer")
        self.status = PLAN_STATUS_CONFIRMED

    def cancel(self) -> None:
        self.status = PLAN_STATUS_CANCELLED

    def complete(self) -> None:
        if self.status != PLAN_STATUS_CONFIRMED:
            raise InvalidUserDataException("Only confirmed sessions can be completed")
        self.status = PLAN_STATUS_COMPLETED

    def cost(self) -> float:
        return self.trainer.session_cost(self.duration_minutes / MINUTES_PER_HOUR)

    def is_upcoming(self, now: datetime) -> bool:
        return self.scheduled_at > now and self.status != PLAN_STATUS_CANCELLED
