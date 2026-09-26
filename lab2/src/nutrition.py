"""Nutrition values and tracker for the culinary domain."""
from __future__ import annotations

from dataclasses import dataclass

from .exceptions import InvalidQuantityError


@dataclass(frozen=True)
class Nutrition:
    """Nutrition content per 100 g (or 100 ml) of a product.

    All values are non-negative. Kilocalories are computed from macros.
    """

    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float = 0.0

    PROTEIN_KCAL_PER_G = 4.0
    FAT_KCAL_PER_G = 9.0
    CARBS_KCAL_PER_G = 4.0

    def __post_init__(self) -> None:
        for name, value in (
            ("protein_g", self.protein_g),
            ("fat_g", self.fat_g),
            ("carbs_g", self.carbs_g),
            ("fiber_g", self.fiber_g),
        ):
            if value < 0:
                raise InvalidQuantityError(f"{name} must be non-negative")

    def kcal(self) -> float:
        """Return total calories per 100 g."""
        return (
            self.protein_g * self.PROTEIN_KCAL_PER_G
            + self.fat_g * self.FAT_KCAL_PER_G
            + self.carbs_g * self.CARBS_KCAL_PER_G
        )

    def is_low_carb(self) -> bool:
        """Return True if carbs are below 10 g per 100 g."""
        return self.carbs_g < 10.0

    def is_high_protein(self) -> bool:
        """Return True if protein is at least 20 g per 100 g."""
        return self.protein_g >= 20.0

    def scale(self, factor: float) -> "Nutrition":
        """Return nutrition for ``factor`` x 100 g."""
        return Nutrition(
            self.protein_g * factor,
            self.fat_g * factor,
            self.carbs_g * factor,
            self.fiber_g * factor,
        )

    def __add__(self, other: "Nutrition") -> "Nutrition":
        return Nutrition(
            self.protein_g + other.protein_g,
            self.fat_g + other.fat_g,
            self.carbs_g + other.carbs_g,
            self.fiber_g + other.fiber_g,
        )


class NutritionTracker:
    """Accumulates nutrition values over a day."""

    def __init__(self, daily_kcal_limit: float = 2000.0) -> None:
        self._limit = daily_kcal_limit
        self._entries: list[Nutrition] = []

    def add(self, nutrition: Nutrition) -> None:
        """Add one nutrition entry."""
        self._entries.append(nutrition)

    def total(self) -> Nutrition:
        """Return the sum of all entries."""
        result = Nutrition(0.0, 0.0, 0.0, 0.0)
        for entry in self._entries:
            result = result + entry
        return result

    def remaining_kcal(self) -> float:
        """Return how many kcal remain within the daily limit."""
        return max(0.0, self._limit - self.total().kcal())

    def is_over_limit(self) -> bool:
        """Return True if the total exceeds the daily limit."""
        return self.total().kcal() > self._limit

    def reset(self) -> None:
        """Clear all entries."""
        self._entries.clear()

    def entry_count(self) -> int:
        """Return the number of entries."""
        return len(self._entries)

    def protein_share(self) -> float:
        """Return the fraction of calories coming from protein."""
        total = self.total().kcal()
        if total == 0:
            return 0.0
        protein_kcal = self.total().protein_g * Nutrition.PROTEIN_KCAL_PER_G
        return protein_kcal / total
