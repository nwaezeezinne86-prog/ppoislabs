"""GPS routes and cardio activities."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import TYPE_CHECKING

from .constants import (
    CYCLING_MET, EARTH_RADIUS_KM, KCAL_PER_MET_KG_HOUR, MAX_LATITUDE, MAX_LONGITUDE, METERS_PER_KM,
    MINUTES_PER_HOUR, MIN_LATITUDE, MIN_LONGITUDE, RUNNING_MET, SWIMMING_MET,
)
from .exceptions import InvalidMeasurementException, InvalidWorkoutException

if TYPE_CHECKING:
    from .users import User


@dataclass
class GPSPoint:
    """A geographic position."""

    latitude: float
    longitude: float
    altitude_m: float
    timestamp: datetime

    def validate(self) -> None:
        if not MIN_LATITUDE <= self.latitude <= MAX_LATITUDE:
            raise InvalidMeasurementException(f"Latitude out of range: {self.latitude}")
        if not MIN_LONGITUDE <= self.longitude <= MAX_LONGITUDE:
            raise InvalidMeasurementException(f"Longitude out of range: {self.longitude}")

    def distance_to(self, other: GPSPoint) -> float:
        lat_from, lat_to = radians(self.latitude), radians(other.latitude)
        delta_lat = lat_to - lat_from
        delta_lon = radians(other.longitude - self.longitude)
        haversine = sin(delta_lat / 2) ** 2 + cos(lat_from) * cos(lat_to) * sin(delta_lon / 2) ** 2
        return 2 * EARTH_RADIUS_KM * asin(sqrt(haversine))

    def elevation_change(self, other: GPSPoint) -> float:
        return other.altitude_m - self.altitude_m


@dataclass
class Route:
    """An ordered track of GPS points."""

    name: str
    points: list[GPSPoint] = field(default_factory=list)

    def add_point(self, point: GPSPoint) -> None:
        point.validate()
        self.points.append(point)

    def point_count(self) -> int:
        return len(self.points)

    def total_distance_km(self) -> float:
        return sum(first.distance_to(second) for first, second in zip(self.points, self.points[1:]))

    def elevation_gain_m(self) -> float:
        changes = (first.elevation_change(second) for first, second in zip(self.points, self.points[1:]))
        return sum(change for change in changes if change > 0)


@dataclass
class CardioActivity:
    """A generic cardio session."""

    activity_id: int
    user: User
    started_at: datetime
    duration_minutes: float
    distance_km: float
    route: Route | None = None

    def intensity_met(self) -> float:
        return RUNNING_MET

    def validate(self) -> None:
        if self.duration_minutes <= 0 or self.distance_km < 0:
            raise InvalidWorkoutException("Duration must be positive and distance non-negative")

    def average_speed_kmh(self) -> float:
        return self.distance_km / (self.duration_minutes / MINUTES_PER_HOUR)

    def pace_min_per_km(self) -> float:
        if self.distance_km == 0:
            raise InvalidWorkoutException("Pace is undefined for zero distance")
        return self.duration_minutes / self.distance_km

    def calories_burned(self) -> float:
        hours = self.duration_minutes / MINUTES_PER_HOUR
        return self.intensity_met() * self.user.profile.weight_kg * hours * KCAL_PER_MET_KG_HOUR


@dataclass
class Running(CardioActivity):
    """A run with cadence data."""

    cadence_spm: int = 0

    def intensity_met(self) -> float:
        return RUNNING_MET

    def estimated_steps(self) -> int:
        return round(self.cadence_spm * self.duration_minutes)


@dataclass
class Cycling(CardioActivity):
    """A bike ride with elevation data."""

    elevation_gain_m: float = 0.0

    def intensity_met(self) -> float:
        return CYCLING_MET

    def climbing_ratio(self) -> float:
        if self.distance_km == 0:
            return 0.0
        return self.elevation_gain_m / (self.distance_km * METERS_PER_KM)


@dataclass
class Swimming(CardioActivity):
    """A pool swim counted in laps."""

    laps: int = 0
    pool_length_m: float = 0.0

    def intensity_met(self) -> float:
        return SWIMMING_MET

    def pool_distance_km(self) -> float:
        return self.laps * self.pool_length_m / METERS_PER_KM

    def laps_per_minute(self) -> float:
        return self.laps / self.duration_minutes
