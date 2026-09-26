"""Cooking techniques for the culinary domain."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .exceptions import OvercookedError


class Technique(ABC):
    """Base class for every cooking technique."""

    def __init__(self, name: str, default_minutes: int) -> None:
        if default_minutes <= 0:
            raise ValueError("Technique duration must be positive")
        self._name = name
        self._default_minutes = default_minutes

    @property
    def name(self) -> str:
        """Human-readable name of the technique."""
        return self._name

    @property
    def default_minutes(self) -> int:
        """Recommended duration in minutes."""
        return self._default_minutes

    @abstractmethod
    def apply(self, ingredient_name: str, minutes: int) -> str:
        """Apply the technique and return a short description of the result."""

    def describe(self) -> str:
        """Return a one-line description."""
        return f"{self._name} ({self._default_minutes} min recommended)"

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._name!r}, {self._default_minutes})"


class Boil(Technique):
    """Boil an ingredient in water."""

    def __init__(self, default_minutes: int = 15, water_ml: int = 1000) -> None:
        super().__init__("boil", default_minutes)
        self._water_ml = water_ml

    def apply(self, ingredient_name: str, minutes: int) -> str:
        if minutes > self._default_minutes * 3:
            raise OvercookedError(f"Boiling {ingredient_name} for {minutes} min")
        return f"Boiled {ingredient_name} for {minutes} min in {self._water_ml} ml of water"

    def scale_water(self, factor: float) -> int:
        """Scale the water amount by a factor."""
        return max(0, round(self._water_ml * factor))


class Fry(Technique):
    """Fry an ingredient in oil."""

    def __init__(self, default_minutes: int = 8, oil_ml: int = 30) -> None:
        super().__init__("fry", default_minutes)
        self._oil_ml = oil_ml

    def apply(self, ingredient_name: str, minutes: int) -> str:
        if minutes > self._default_minutes * 2:
            raise OvercookedError(f"Frying {ingredient_name} for {minutes} min")
        return f"Fried {ingredient_name} for {minutes} min in {self._oil_ml} ml of oil"

    def is_deep_fry(self) -> bool:
        """Return True if the technique uses more than 200 ml of oil."""
        return self._oil_ml > 200


class Bake(Technique):
    """Bake an ingredient in an oven."""

    def __init__(self, default_minutes: int = 30, temperature_c: int = 180) -> None:
        super().__init__("bake", default_minutes)
        self._temperature_c = temperature_c

    def apply(self, ingredient_name: str, minutes: int) -> str:
        if minutes > self._default_minutes * 3:
            raise OvercookedError(f"Baking {ingredient_name} for {minutes} min")
        return f"Baked {ingredient_name} for {minutes} min at {self._temperature_c} C"

    def lower_temperature(self, delta: int) -> None:
        """Reduce the baking temperature, never below 60 C."""
        self._temperature_c = max(60, self._temperature_c - delta)


class Grill(Technique):
    """Grill an ingredient on an open flame."""

    def __init__(self, default_minutes: int = 10, flame_level: int = 5) -> None:
        super().__init__("grill", default_minutes)
        self._flame_level = max(1, min(10, flame_level))

    def apply(self, ingredient_name: str, minutes: int) -> str:
        if minutes > self._default_minutes * 2:
            raise OvercookedError(f"Grilling {ingredient_name} for {minutes} min")
        return f"Grilled {ingredient_name} for {minutes} min at flame {self._flame_level}"

    def is_high_heat(self) -> bool:
        """Return True if the flame level is high."""
        return self._flame_level >= 8


class Steam(Technique):
    """Steam an ingredient."""

    def __init__(self, default_minutes: int = 12, pressure_bar: float = 1.0) -> None:
        super().__init__("steam", default_minutes)
        self._pressure_bar = pressure_bar

    def apply(self, ingredient_name: str, minutes: int) -> str:
        if minutes > self._default_minutes * 3:
            raise OvercookedError(f"Steaming {ingredient_name} for {minutes} min")
        return f"Steamed {ingredient_name} for {minutes} min at {self._pressure_bar} bar"

    def is_pressure_cooking(self) -> bool:
        """Return True if the pressure is above 1.5 bar."""
        return self._pressure_bar > 1.5


class SousVide(Technique):
    """Sous-vide cooking in a water bath."""

    def __init__(self, default_minutes: int = 60, temperature_c: int = 60) -> None:
        super().__init__("sous-vide", default_minutes)
        self._temperature_c = temperature_c

    def apply(self, ingredient_name: str, minutes: int) -> str:
        if minutes < self._default_minutes:
            raise OvercookedError(
                f"Sous-vide too short: {minutes} < {self._default_minutes}"
            )
        return f"Sous-vide {ingredient_name} for {minutes} min at {self._temperature_c} C"

    def is_low_temp(self) -> bool:
        """Return True if the water bath is below 70 C."""
        return self._temperature_c < 70


class Mix(Technique):
    """Mixing or whipping ingredients."""

    def __init__(self, default_minutes: int = 5, speed: int = 2) -> None:
        super().__init__("mix", default_minutes)
        self._speed = max(1, min(5, speed))

    def apply(self, ingredient_name: str, minutes: int) -> str:
        return f"Mixed {ingredient_name} for {minutes} min at speed {self._speed}"

    def is_high_speed(self) -> bool:
        """Return True if the mixing speed is high."""
        return self._speed >= 4
