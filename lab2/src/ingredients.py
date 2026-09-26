"""Ingredient hierarchy for the culinary domain."""
from __future__ import annotations

from datetime import date

from .allergens import AllergenSet
from .exceptions import InvalidQuantityError
from .money import Money
from .units import Quantity, Unit


class Ingredient:
    """Base class for every ingredient in the domain."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        allergens: AllergenSet | None = None,
    ) -> None:
        if not name.strip():
            raise InvalidQuantityError("Ingredient name must not be empty")
        self._name = name
        self._unit = unit
        self._price_per_unit = price_per_unit
        self._allergens = allergens or AllergenSet()

    @property
    def name(self) -> str:
        """Human-readable name."""
        return self._name

    @property
    def unit(self) -> Unit:
        """Reference unit for this ingredient."""
        return self._unit

    @property
    def allergens(self) -> AllergenSet:
        """Allergens present in this ingredient."""
        return self._allergens

    def price_for(self, quantity: Quantity) -> Money:
        """Return the price of ``quantity`` of this ingredient."""
        converted = quantity.to(self._unit)
        return self._price_per_unit * converted.amount

    def describe(self) -> str:
        """Return a one-line description used in menus and reports."""
        return f"{self._name} ({self._unit.value}), {self._price_per_unit}/unit"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ingredient):
            return NotImplemented
        return self._name.lower() == other._name.lower()

    def __hash__(self) -> int:
        return hash(self._name.lower())

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._name!r})"


class Vegetable(Ingredient):
    """Vegetable with a seasonal availability window."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        season_start_month: int,
        season_end_month: int,
        organic: bool = False,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._season_start_month = season_start_month
        self._season_end_month = season_end_month
        self._organic = organic

    def is_in_season(self, today: date) -> bool:
        """Return True if ``today`` falls inside the season window."""
        month = today.month
        if self._season_start_month <= self._season_end_month:
            return self._season_start_month <= month <= self._season_end_month
        return month >= self._season_start_month or month <= self._season_end_month

    def is_organic(self) -> bool:
        """Return True if the vegetable is organic."""
        return self._organic

    def describe(self) -> str:
        kind = "organic" if self._organic else "regular"
        return (
            f"{self._name} [{kind}] season "
            f"{self._season_start_month}-{self._season_end_month}"
        )


class Fruit(Ingredient):
    """Fruit with a ripeness level between 0 and 1."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        sweetness: float,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._sweetness = max(0.0, min(1.0, sweetness))
        self._ripeness = 0.0

    def ripen(self, delta: float) -> None:
        """Advance the ripeness by ``delta``, clamped to [0, 1]."""
        self._ripeness = max(0.0, min(1.0, self._ripeness + delta))

    def is_ripe(self) -> bool:
        """Return True when ripeness is above 0.8."""
        return self._ripeness >= 0.8

    def sweetness_level(self) -> str:
        """Return a human label for the sweetness."""
        if self._sweetness < 0.3:
            return "sour"
        if self._sweetness < 0.7:
            return "balanced"
        return "sweet"


class Meat(Ingredient):
    """Meat with an animal source and recommended cooking temperature."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        animal: str,
        safe_temp_c: int,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._animal = animal
        self._safe_temp_c = safe_temp_c

    def is_safe_temperature(self, measured_c: int) -> bool:
        """Return True if the measured temperature is safe."""
        return measured_c >= self._safe_temp_c

    def recommended_technique(self) -> str:
        """Return a suggested cooking technique based on the animal."""
        mapping = {"beef": "grill", "chicken": "roast", "fish": "steam"}
        return mapping.get(self._animal.lower(), "bake")


class Fish(Ingredient):
    """Fish with a freshness flag and bone count."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        species: str,
        bones: int = 0,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._species = species
        self._bones = max(0, bones)
        self._fresh = True

    def mark_stale(self) -> None:
        """Mark the fish as not fresh."""
        self._fresh = False

    def is_boneless(self) -> bool:
        """Return True if the fish has no bones."""
        return self._bones == 0

    def is_fresh(self) -> bool:
        """Return True while the fish is fresh."""
        return self._fresh


class Dairy(Ingredient):
    """Dairy product with a fat percentage."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        fat_percent: float,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._fat_percent = max(0.0, min(100.0, fat_percent))

    def is_low_fat(self) -> bool:
        """Return True if fat content is below 5 %."""
        return self._fat_percent < 5.0

    def scaled_fat(self, factor: float) -> float:
        """Return fat percentage for a scaled amount, capped at 100."""
        return min(100.0, self._fat_percent * factor)


class Spice(Ingredient):
    """Spice with a Scoville heat rating."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        scoville: int,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._scoville = max(0, scoville)

    def heat_level(self) -> str:
        """Return a human label for the heat level."""
        s = self._scoville
        if s == 0:
            return "mild"
        if s < 2500:
            return "medium"
        if s < 30000:
            return "hot"
        return "extreme"

    def is_hot(self) -> bool:
        """Return True if the spice is hotter than the medium threshold."""
        return self._scoville >= 2500


class Grain(Ingredient):
    """Grain with gluten information and cooking time."""

    def __init__(
        self,
        name: str,
        unit: Unit,
        price_per_unit: Money,
        cooking_minutes: int,
        contains_gluten: bool,
        allergens: AllergenSet | None = None,
    ) -> None:
        super().__init__(name, unit, price_per_unit, allergens)
        self._cooking_minutes = max(1, cooking_minutes)
        self._contains_gluten = contains_gluten

    def is_gluten_free(self) -> bool:
        """Return True if the grain is gluten-free."""
        return not self._contains_gluten

    def scale_cooking_time(self, factor: float) -> int:
        """Return scaled cooking time in minutes."""
        return max(1, round(self._cooking_minutes * factor))


class IngredientLot:
    """A batch of an ingredient with a specific expiry date."""

    def __init__(
        self,
        ingredient: Ingredient,
        quantity: Quantity,
        expiry: date,
    ) -> None:
        self._ingredient = ingredient
        self._quantity = quantity
        self._expiry = expiry

    @property
    def ingredient(self) -> Ingredient:
        """Ingredient this lot refers to."""
        return self._ingredient

    @property
    def quantity(self) -> Quantity:
        """Remaining quantity in the lot."""
        return self._quantity

    def is_expired(self, today: date) -> bool:
        """Return True if today is past the expiry date."""
        return today > self._expiry

    def days_until_expiry(self, today: date) -> int:
        """Return days remaining until expiry (can be negative)."""
        return (self._expiry - today).days

    def consume(self, amount: Quantity) -> None:
        """Reduce the lot by ``amount``; raise if not enough remains."""
        if amount.amount > self._quantity.amount:
            raise InvalidQuantityError("Not enough in the lot")
        self._quantity = Quantity(
            self._quantity.amount - amount.amount, self._quantity.unit
        )

    def is_empty(self) -> bool:
        """Return True if the lot has no quantity left."""
        return self._quantity.is_zero()
