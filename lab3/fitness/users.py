"""User accounts, profiles, body measurements and subscriptions."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from .constants import (
    ACTIVITY_MULTIPLIERS, CM_PER_METER, DAYS_PER_MONTH, DEFAULT_ACTIVITY_LEVEL, EMAIL_PATTERN, GENDERS,
    MAX_AGE_YEARS, MAX_BODY_FAT_PERCENT, MAX_HEIGHT_CM, MAX_WEIGHT_KG, MIN_AGE_YEARS, MIN_HEIGHT_CM,
    MIN_NAME_LENGTH, MIN_PASSWORD_LENGTH, MIN_WEIGHT_KG, PBKDF2_ITERATIONS, PERCENT,
)
from .exceptions import (
    AuthenticationException, InvalidMeasurementException, InvalidUserDataException,
    SubscriptionRequiredException,
)


@dataclass
class UserProfile:
    """Physical parameters of a user."""

    height_cm: float
    weight_kg: float
    gender: str
    activity_level: str = DEFAULT_ACTIVITY_LEVEL

    def validate(self) -> None:
        if not MIN_HEIGHT_CM <= self.height_cm <= MAX_HEIGHT_CM:
            raise InvalidUserDataException(f"Height out of range: {self.height_cm}")
        if not MIN_WEIGHT_KG <= self.weight_kg <= MAX_WEIGHT_KG:
            raise InvalidUserDataException(f"Weight out of range: {self.weight_kg}")
        if self.gender not in GENDERS:
            raise InvalidUserDataException(f"Unknown gender: {self.gender}")
        if self.activity_level not in ACTIVITY_MULTIPLIERS:
            raise InvalidUserDataException(f"Unknown activity level: {self.activity_level}")

    def height_m(self) -> float:
        return self.height_cm / CM_PER_METER

    def activity_multiplier(self) -> float:
        return ACTIVITY_MULTIPLIERS[self.activity_level]

    def update_weight(self, new_weight_kg: float) -> None:
        if not MIN_WEIGHT_KG <= new_weight_kg <= MAX_WEIGHT_KG:
            raise InvalidMeasurementException(f"Weight out of range: {new_weight_kg}")
        self.weight_kg = new_weight_kg


@dataclass
class Account:
    """Login credentials of a user."""

    login: str
    password_hash: str
    created_at: datetime
    is_active: bool = True

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
        return digest.hex()

    @staticmethod
    def is_strong_password(password: str) -> bool:
        has_letter = any(char.isalpha() for char in password)
        has_digit = any(char.isdigit() for char in password)
        return len(password) >= MIN_PASSWORD_LENGTH and has_letter and has_digit

    @classmethod
    def create(cls, login: str, password: str, created_at: datetime) -> Account:
        if not cls.is_strong_password(password):
            raise InvalidUserDataException("Password must be 8+ characters with letters and digits")
        return cls(login, cls.hash_password(password, login), created_at)

    def check_password(self, password: str) -> bool:
        return self.hash_password(password, self.login) == self.password_hash

    def authenticate(self, password: str) -> None:
        if not self.is_active or not self.check_password(password):
            raise AuthenticationException("Invalid login or password")

    def change_password(self, old_password: str, new_password: str) -> None:
        self.authenticate(old_password)
        if not self.is_strong_password(new_password):
            raise InvalidUserDataException("New password is too weak")
        self.password_hash = self.hash_password(new_password, self.login)

    def deactivate(self) -> None:
        self.is_active = False


@dataclass
class BodyMeasurement:
    """A dated record of body composition."""

    measured_on: date
    weight_kg: float
    body_fat_percent: float
    waist_cm: float

    def validate(self) -> None:
        if not MIN_WEIGHT_KG <= self.weight_kg <= MAX_WEIGHT_KG:
            raise InvalidMeasurementException(f"Weight out of range: {self.weight_kg}")
        if not 0 <= self.body_fat_percent <= MAX_BODY_FAT_PERCENT:
            raise InvalidMeasurementException(f"Body fat out of range: {self.body_fat_percent}")
        if self.waist_cm <= 0:
            raise InvalidMeasurementException("Waist must be positive")

    def fat_mass_kg(self) -> float:
        return self.weight_kg * self.body_fat_percent / PERCENT

    def lean_mass_kg(self) -> float:
        return self.weight_kg - self.fat_mass_kg()


@dataclass
class SubscriptionPlan:
    """A purchasable plan with its feature set."""

    name: str
    monthly_price: float
    includes_coaching: bool
    max_challenges: int

    def total_price(self, months: int) -> float:
        if months <= 0:
            raise InvalidUserDataException("Months must be positive")
        return self.monthly_price * months

    def allows_coaching(self) -> bool:
        return self.includes_coaching

    def allows_challenges(self, joined_count: int) -> bool:
        return joined_count < self.max_challenges


@dataclass
class Subscription:
    """A plan bought by a user for a period."""

    plan: SubscriptionPlan
    start_date: date
    end_date: date
    auto_renew: bool = False

    def is_active(self, today: date) -> bool:
        return self.start_date <= today <= self.end_date

    def days_left(self, today: date) -> int:
        return max((self.end_date - today).days, 0)

    def ensure_active(self, today: date) -> None:
        if not self.is_active(today):
            raise SubscriptionRequiredException("Subscription is not active")

    def renew(self, months: int) -> None:
        if months <= 0:
            raise InvalidUserDataException("Months must be positive")
        self.end_date += timedelta(days=months * DAYS_PER_MONTH)

    def cancel_auto_renew(self) -> None:
        self.auto_renew = False


@dataclass
class User:
    """A registered person who tracks fitness data."""

    user_id: int
    name: str
    email: str
    birth_date: date
    account: Account
    profile: UserProfile
    measurements: list[BodyMeasurement] = field(default_factory=list)
    subscription: Subscription | None = None

    def validate(self, today: date) -> None:
        if len(self.name.strip()) < MIN_NAME_LENGTH:
            raise InvalidUserDataException("Name is too short")
        if not self.has_valid_email():
            raise InvalidUserDataException(f"Invalid email: {self.email}")
        if not MIN_AGE_YEARS <= self.age(today) <= MAX_AGE_YEARS:
            raise InvalidUserDataException("Age is out of the allowed range")
        self.profile.validate()

    def has_valid_email(self) -> bool:
        return EMAIL_PATTERN.fullmatch(self.email) is not None

    def age(self, today: date) -> int:
        years = today.year - self.birth_date.year
        had_birthday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return years if had_birthday else years - 1

    def record_measurement(self, measurement: BodyMeasurement) -> None:
        measurement.validate()
        self.measurements.append(measurement)
        self.profile.update_weight(measurement.weight_kg)

    def latest_measurement(self) -> BodyMeasurement | None:
        return self.measurements[-1] if self.measurements else None

    def weight_change(self) -> float:
        if len(self.measurements) < 2:
            return 0.0
        return self.measurements[-1].weight_kg - self.measurements[0].weight_kg

    def subscribe(self, subscription: Subscription) -> None:
        self.subscription = subscription

    def has_active_subscription(self, today: date) -> bool:
        return self.subscription is not None and self.subscription.is_active(today)
