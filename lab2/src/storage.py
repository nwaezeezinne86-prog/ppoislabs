"""Storage: warehouses, zones, storage units, racks."""
from __future__ import annotations

from datetime import date

from .exceptions import InvalidQuantityError
from .ingredients import IngredientLot
from .units import Quantity

KILOGRAMS_PER_GRAM = 1000.0


class Rack:
    """A rack inside a storage zone."""

    def __init__(self, code: str, shelf_count: int, max_weight_kg: float) -> None:
        if shelf_count <= 0:
            raise InvalidQuantityError("Shelf count must be positive")
        self._code = code
        self._shelf_count = shelf_count
        self._max_weight_kg = max_weight_kg
        self._current_weight_kg = 0.0

    @property
    def code(self) -> str:
        """Rack code."""
        return self._code

    def can_hold(self, weight_kg: float) -> bool:
        """Return True if the rack can accept the additional weight."""
        return self._current_weight_kg + weight_kg <= self._max_weight_kg

    def add_weight(self, weight_kg: float) -> None:
        """Add weight; raise if the rack would be overloaded."""
        if not self.can_hold(weight_kg):
            raise InvalidQuantityError("Rack would be overloaded")
        self._current_weight_kg += weight_kg

    def remove_weight(self, weight_kg: float) -> None:
        """Remove weight; never goes below zero."""
        self._current_weight_kg = max(0.0, self._current_weight_kg - weight_kg)

    def utilization(self) -> float:
        """Return current weight as a fraction of maximum."""
        if self._max_weight_kg == 0:
            return 0.0
        return self._current_weight_kg / self._max_weight_kg

    def describe(self) -> str:
        return (
            f"Rack {self._code} "
            f"({self._current_weight_kg:.1f}/{self._max_weight_kg:.1f} kg)"
        )


class StorageZone:
    """A zone of a warehouse that contains racks."""

    def __init__(self, name: str, temperature_c: int) -> None:
        self._name = name
        self._temperature_c = temperature_c
        self._racks: list[Rack] = []

    @property
    def name(self) -> str:
        """Zone name."""
        return self._name

    @property
    def temperature_c(self) -> int:
        """Zone temperature."""
        return self._temperature_c

    def add_rack(self, rack: Rack) -> None:
        """Add a rack to the zone."""
        self._racks.append(rack)

    def remove_rack(self, code: str) -> None:
        """Remove a rack by code."""
        self._racks = [r for r in self._racks if r.code != code]

    def rack_count(self) -> int:
        """Return the number of racks."""
        return len(self._racks)

    def is_cold(self) -> bool:
        """Return True for zones below 8 C."""
        return self._temperature_c < 8

    def find_rack(self, code: str) -> Rack | None:
        """Return a rack by code or None."""
        for r in self._racks:
            if r.code == code:
                return r
        return None

    def describe(self) -> str:
        kind = "cold" if self.is_cold() else "ambient"
        return (
            f"Zone '{self._name}' ({kind}, {self._temperature_c} C, "
            f"{self.rack_count()} racks)"
        )


class StorageUnit:
    """A storage unit holding ingredient lots."""

    def __init__(self, name: str, capacity_kg: float) -> None:
        if capacity_kg <= 0:
            raise InvalidQuantityError("Capacity must be positive")
        self._name = name
        self._capacity_kg = capacity_kg
        self._lots: list[IngredientLot] = []

    @property
    def name(self) -> str:
        """Unit name."""
        return self._name

    def store(self, lot: IngredientLot) -> None:
        """Store a lot if there is room."""
        current_kg = self._total_kg()
        incoming_kg = lot.quantity.amount / KILOGRAMS_PER_GRAM
        if current_kg + incoming_kg > self._capacity_kg:
            raise InvalidQuantityError("Storage unit is full")
        self._lots.append(lot)

    def take(self, ingredient_name: str, amount: Quantity) -> IngredientLot:
        """Take from the newest lot of the ingredient that has enough."""
        for lot in reversed(self._lots):
            same = lot.ingredient.name == ingredient_name
            enough = lot.quantity.amount >= amount.amount
            if same and enough:
                lot.consume(amount)
                if lot.is_empty():
                    self._lots.remove(lot)
                return lot
        raise InvalidQuantityError(
            f"Not enough {ingredient_name} in {self._name}"
        )

    def _total_kg(self) -> float:
        return sum(l.quantity.amount / KILOGRAMS_PER_GRAM for l in self._lots)

    def utilization(self) -> float:
        """Return utilization 0-1."""
        if self._capacity_kg == 0:
            return 0.0
        return self._total_kg() / self._capacity_kg

    def expired_lots(self, today: date) -> list[IngredientLot]:
        """Return expired lots in this unit."""
        return [l for l in self._lots if l.is_expired(today)]

    def purge_expired(self, today: date) -> int:
        """Remove expired lots; return the number removed."""
        expired = self.expired_lots(today)
        for lot in expired:
            self._lots.remove(lot)
        return len(expired)

    def lot_count(self) -> int:
        """Return the number of lots in the unit."""
        return len(self._lots)

    def describe(self) -> str:
        return (
            f"StorageUnit '{self._name}' "
            f"({self.utilization() * 100:.0f}% full, {self.lot_count()} lots)"
        )


class Warehouse:
    """A warehouse with zones and an address."""

    def __init__(self, name: str, address: str) -> None:
        self._name = name
        self._address = address
        self._zones: list[StorageZone] = []

    @property
    def name(self) -> str:
        """Warehouse name."""
        return self._name

    @property
    def address(self) -> str:
        """Physical address."""
        return self._address

    def add_zone(self, zone: StorageZone) -> None:
        """Add a zone."""
        self._zones.append(zone)

    def remove_zone(self, name: str) -> None:
        """Remove a zone by name."""
        self._zones = [z for z in self._zones if z.name != name]

    def zone_count(self) -> int:
        """Return the number of zones."""
        return len(self._zones)

    def total_racks(self) -> int:
        """Return total number of racks across all zones."""
        return sum(z.rack_count() for z in self._zones)

    def cold_zones(self) -> list[StorageZone]:
        """Return only the cold zones."""
        return [z for z in self._zones if z.is_cold()]

    def find_zone(self, name: str) -> StorageZone | None:
        """Return a zone by name or None."""
        for z in self._zones:
            if z.name == name:
                return z
        return None

    def describe(self) -> str:
        return (
            f"Warehouse '{self._name}' at {self._address} "
            f"({self.zone_count()} zones, {self.total_racks()} racks)"
        )
