"""Allergens and allergen sets used in the culinary domain."""
from __future__ import annotations

from enum import Enum
from typing import Iterable

from .exceptions import AllergenConflictError


class Allergen(str, Enum):
    """Common food allergens."""

    GLUTEN = "gluten"
    LACTOSE = "lactose"
    NUTS = "nuts"
    PEANUTS = "peanuts"
    EGGS = "eggs"
    SOY = "soy"
    FISH = "fish"
    SHELLFISH = "shellfish"
    SESAME = "sesame"


class AllergenSet:
    """A set of allergens, with helpful membership checks."""

    def __init__(self, allergens: Iterable[Allergen] | None = None) -> None:
        self._items: set[Allergen] = set(allergens or ())

    def add(self, allergen: Allergen) -> None:
        """Add one allergen to the set."""
        self._items.add(allergen)

    def remove(self, allergen: Allergen) -> None:
        """Remove one allergen from the set, if present."""
        self._items.discard(allergen)

    def contains(self, allergen: Allergen) -> bool:
        """Return True if the allergen is present."""
        return allergen in self._items

    def union(self, other: "AllergenSet") -> "AllergenSet":
        """Return a new set containing both sets' allergens."""
        return AllergenSet(self._items | other._items)

    def intersects(self, other: "AllergenSet") -> bool:
        """Return True if the two sets share at least one allergen."""
        return bool(self._items & other._items)

    def is_empty(self) -> bool:
        """Return True if there are no allergens."""
        return not self._items

    def check_compatibility(self, restriction: "AllergenSet") -> None:
        """Raise AllergenConflictError if this set violates ``restriction``."""
        if self.intersects(restriction):
            shared = self._items & restriction._items
            names = ", ".join(a.value for a in shared)
            raise AllergenConflictError(f"Contains forbidden allergens: {names}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AllergenSet):
            return NotImplemented
        return self._items == other._items

    def __hash__(self) -> int:
        return hash(frozenset(self._items))

    def __str__(self) -> str:
        if not self._items:
            return "(no allergens)"
        return ", ".join(sorted(a.value for a in self._items))

    def __repr__(self) -> str:
        return f"AllergenSet({sorted(a.value for a in self._items)!r})"

    def as_set(self) -> set[Allergen]:
        """Return a copy of the underlying set."""
        return set(self._items)
