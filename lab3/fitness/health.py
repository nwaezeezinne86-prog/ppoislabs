"""Heart rate, sleep, steps and hydration tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from .constants import (
    DEFAULT_HYDRATION_GOAL_ML, DEFAULT_STEP_GOAL, DEFAULT_STRIDE_M, DAYS_PER_WEEK, FAIR_SLEEP_QUALITY,
    GOOD_SLEEP_QUALITY, HEART_RATE_ZONES, MAX_BPM, MAX_HEART_RATE_BASE, MAX_QUALITY_SCORE, METERS_PER_KM,
    MIN_BPM, MIN_SLEEP_HOURS, SECONDS_PER_HOUR,
)
from .exceptions import InvalidMeasurementException

if TYPE_CHECKING:
    from .devices import Device
    from .users import User


@dataclass
class HeartRateReading:
    """A single pulse measurement."""

    bpm: int
    timestamp: datetime

    def validate(self) -> None:
        if not MIN_BPM <= self.bpm <= MAX_BPM:
            raise InvalidMeasurementException(f"Heart rate out of range: {self.bpm}")


@dataclass
class HeartRateZone:
    """A named pulse range."""

    name: str
    min_bpm: int
    max_bpm: int

    def contains(self, bpm: int) -> bool:
        return self.min_bpm <= bpm <= self.max_bpm


@dataclass
class HeartRateMonitor:
    """Collects heart rate readings from a device."""

    device: Device
    readings: list[HeartRateReading] = field(default_factory=list)
    zones: list[HeartRateZone] = field(default_factory=list)

    @staticmethod
    def zones_for_age(age: int) -> list[HeartRateZone]:
        max_rate = MAX_HEART_RATE_BASE - age
        return [HeartRateZone(name, round(max_rate * low), round(max_rate * high))
                for name, low, high in HEART_RATE_ZONES]

    def record(self, reading: HeartRateReading) -> None:
        self.device.require_connected()
        reading.validate()
        self.readings.append(reading)

    def average_bpm(self) -> float:
        if not self.readings:
            return 0.0
        return sum(item.bpm for item in self.readings) / len(self.readings)

    def peak_bpm(self) -> int:
        return max((item.bpm for item in self.readings), default=0)

    def resting_bpm(self) -> int:
        return min((item.bpm for item in self.readings), default=0)

    def zone_for(self, bpm: int) -> HeartRateZone | None:
        for zone in self.zones:
            if zone.contains(bpm):
                return zone
        return None

    def readings_in_zone(self, zone: HeartRateZone) -> int:
        return sum(1 for item in self.readings if zone.contains(item.bpm))


@dataclass
class SleepRecord:
    """One night of sleep."""

    user: User
    sleep_start: datetime
    sleep_end: datetime
    quality_score: int

    def validate(self) -> None:
        if self.sleep_end <= self.sleep_start:
            raise InvalidMeasurementException("Sleep must end after it starts")
        if not 0 <= self.quality_score <= MAX_QUALITY_SCORE:
            raise InvalidMeasurementException("Quality score out of range")

    def duration_hours(self) -> float:
        return (self.sleep_end - self.sleep_start).total_seconds() / SECONDS_PER_HOUR

    def is_sufficient(self) -> bool:
        return self.duration_hours() >= MIN_SLEEP_HOURS

    def quality_label(self) -> str:
        if self.quality_score >= GOOD_SLEEP_QUALITY:
            return "good"
        return "fair" if self.quality_score >= FAIR_SLEEP_QUALITY else "poor"


@dataclass
class StepCounter:
    """Daily step totals."""

    steps_by_day: dict[date, int] = field(default_factory=dict)
    daily_goal: int = DEFAULT_STEP_GOAL
    stride_m: float = DEFAULT_STRIDE_M

    def add_steps(self, day: date, count: int) -> None:
        if count < 0:
            raise InvalidMeasurementException("Step count cannot be negative")
        self.steps_by_day[day] = self.steps_on(day) + count

    def steps_on(self, day: date) -> int:
        return self.steps_by_day.get(day, 0)

    def goal_reached(self, day: date) -> bool:
        return self.steps_on(day) >= self.daily_goal

    def weekly_total(self, last_day: date) -> int:
        days = (last_day - timedelta(days=offset) for offset in range(DAYS_PER_WEEK))
        return sum(self.steps_on(day) for day in days)

    def distance_km(self, day: date) -> float:
        return self.steps_on(day) * self.stride_m / METERS_PER_KM


@dataclass
class HydrationEntry:
    """A glass of water or other drink."""

    volume_ml: int
    timestamp: datetime


@dataclass
class HydrationLog:
    """Tracks water intake against a daily goal."""

    entries: list[HydrationEntry] = field(default_factory=list)
    daily_goal_ml: int = DEFAULT_HYDRATION_GOAL_ML

    def add_entry(self, entry: HydrationEntry) -> None:
        if entry.volume_ml <= 0:
            raise InvalidMeasurementException("Volume must be positive")
        self.entries.append(entry)

    def total_on(self, day: date) -> int:
        return sum(item.volume_ml for item in self.entries if item.timestamp.date() == day)

    def remaining_on(self, day: date) -> int:
        return max(self.daily_goal_ml - self.total_on(day), 0)

    def goal_reached(self, day: date) -> bool:
        return self.total_on(day) >= self.daily_goal_ml
