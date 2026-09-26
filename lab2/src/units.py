"""Measurement units and conversions for the culinary domain."""
from __future__ import annotations

from enum import Enum

from .exceptions import InvalidQuantityError, InvalidUnitError


class Unit(str, Enum):
    """Supported units of measurement."""

    GRAM = "g"
    KILOGRAM = "kg"
    MILLILITER = "ml"
    LITER = "l"
    PIECE = "pc"
    TEASPOON = "tsp"
    TABLESPOON = "tbsp"
    CUP = "cup"


_MASS_TO_GRAMS = {
    Unit.GRAM: 1.0,
    Unit.KILOGRAM: 1000.0,
}

_VOLUME_TO_ML = {
    Unit.MILLILITER: 1.0,
    Unit.LITER: 1000.0,
    Unit.TEASPOON: 5.0,
    Unit.TABLESPOON: 15.0,
    Unit.CUP: 240.0,
}

_COUNT_UNITS = {Unit.PIECE}


def is_mass(unit: Unit) -> bool:
    """Return True if the unit measures mass."""
    return unit in _MASS_TO_GRAMS


def is_volume(unit: Unit) -> bool:
    """Return True if the unit measures volume."""
    return unit in _VOLUME_TO_ML


def is_count(unit: Unit) -> bool:
    """Return True if the unit measures a discrete count."""
    return unit in _COUNT_UNITS


def convert(amount: float, src: Unit, dst: Unit) -> float:
    """Convert ``amount`` from ``src`` to ``dst``.

    Raises InvalidUnitError if the units belong to different dimensions.
    """
    if amount < 0:
        raise InvalidQuantityError(f"Negative amount: {amount}")
    if src == dst:
        return amount
    if is_mass(src) and is_mass(dst):
        return amount * _MASS_TO_GRAMS[src] / _MASS_TO_GRAMS[dst]
    if is_volume(src) and is_volume(dst):
        return amount * _VOLUME_TO_ML[src] / _VOLUME_TO_ML[dst]
    if is_count(src) and is_count(dst):
        return amount
    raise InvalidUnitError(f"Cannot convert {src} to {dst}")


def normalize_to_base(amount: float, unit: Unit) -> tuple[float, str]:
    """Return ``(value, base_unit_name)`` where base is g, ml, or pc."""
    if is_mass(unit):
        return amount * _MASS_TO_GRAMS[unit], "g"
    if is_volume(unit):
        return amount * _VOLUME_TO_ML[unit], "ml"
    if is_count(unit):
        return amount, "pc"
    raise InvalidUnitError(f"Unknown unit: {unit}")


class Quantity:
    """An amount together with its measurement unit."""

    def __init__(self, amount: float, unit: Unit) -> None:
        if amount < 0:
            raise InvalidQuantityError(f"Negative amount: {amount}")
        self._amount = float(amount)
        self._unit = unit

    @property
    def amount(self) -> float:
        """Numeric amount."""
        return self._amount

    @property
    def unit(self) -> Unit:
        """Measurement unit."""
        return self._unit

    def to(self, target: Unit) -> "Quantity":
        """Return this quantity expressed in ``target`` units."""
        return Quantity(convert(self._amount, self._unit, target), target)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        try:
            return self.to(other._unit)._amount == other._amount
        except InvalidUnitError:
            return False

    def __hash__(self) -> int:
        return hash((self._amount, self._unit))

    def __str__(self) -> str:
        return f"{self._amount:g} {self._unit.value}"

    def __repr__(self) -> str:
        return f"Quantity({self._amount}, Unit.{self._unit.name})"

    def __add__(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity):
            return NotImplemented
        converted = other.to(self._unit)
        return Quantity(self._amount + converted._amount, self._unit)

    def __mul__(self, factor: float) -> "Quantity":
        return Quantity(self._amount * factor, self._unit)

    def is_zero(self) -> bool:
        """Return True if the amount is zero."""
        return self._amount == 0
