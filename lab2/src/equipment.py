"""Kitchen equipment for the culinary domain."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .exceptions import EquipmentBrokenError, EquipmentUnavailableError


class Equipment(ABC):
    """Base class for every piece of kitchen equipment."""

    def __init__(self, name: str, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._name = name
        self._capacity = capacity
        self._in_use = False
        self._broken = False
        self._total_uses = 0

    @property
    def name(self) -> str:
        """Equipment name."""
        return self._name

    @property
    def capacity(self) -> int:
        """Maximum load the equipment can handle."""
        return self._capacity

    def is_available(self) -> bool:
        """Return True if the equipment is free and working."""
        return not self._in_use and not self._broken

    def mark_broken(self) -> None:
        """Mark the equipment as broken."""
        self._broken = True

    def repair(self) -> None:
        """Return a broken piece of equipment to service."""
        self._broken = False

    def acquire(self) -> None:
        """Acquire the equipment for a task."""
        if self._broken:
            raise EquipmentBrokenError(f"{self._name} is broken")
        if self._in_use:
            raise EquipmentUnavailableError(f"{self._name} is already in use")
        self._in_use = True
        self._total_uses += 1

    def release(self) -> None:
        """Release the equipment after use."""
        self._in_use = False

    def uses(self) -> int:
        """Return the total number of times the equipment was used."""
        return self._total_uses

    @abstractmethod
    def describe(self) -> str:
        """Return a human-readable description of the equipment."""

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._name!r}, capacity={self._capacity})"


class Oven(Equipment):
    """An oven with a temperature range."""

    def __init__(
        self,
        name: str = "Oven",
        capacity: int = 4,
        max_temp_c: int = 300,
    ) -> None:
        super().__init__(name, capacity)
        self._max_temp_c = max_temp_c

    def is_temp_allowed(self, temp_c: int) -> bool:
        """Return True if the requested temperature is within range."""
        return 0 < temp_c <= self._max_temp_c

    def describe(self) -> str:
        return f"Oven up to {self._max_temp_c} C, {self._capacity} trays"


class Stove(Equipment):
    """A stove with a number of burners."""

    def __init__(
        self,
        name: str = "Stove",
        capacity: int = 4,
        burners: int = 4,
    ) -> None:
        super().__init__(name, capacity)
        self._burners = burners
        self._active_burners = 0

    def light_burner(self) -> None:
        """Light one burner; raise if all are already on."""
        if self._active_burners >= self._burners:
            raise EquipmentUnavailableError("All burners are busy")
        self._active_burners += 1

    def extinguish_burner(self) -> None:
        """Turn off one burner."""
        self._active_burners = max(0, self._active_burners - 1)

    def describe(self) -> str:
        return f"Stove with {self._burners} burners"


class Blender(Equipment):
    """A blender with variable speed."""

    def __init__(
        self,
        name: str = "Blender",
        capacity: int = 2,
        max_speed: int = 5,
    ) -> None:
        super().__init__(name, capacity)
        self._max_speed = max_speed

    def describe(self) -> str:
        return f"Blender up to speed {self._max_speed}"


class Machine(Equipment):
    """A generic machine with a program name."""

    def __init__(self, name: str, capacity: int, program: str) -> None:
        super().__init__(name, capacity)
        self._program = program
        self._cycles = 0

    def run_cycle(self) -> None:
        """Run one cycle; requires equipment to be acquired first."""
        if not self._in_use:
            raise EquipmentUnavailableError(f"Acquire {self._name} before running")
        self._cycles += 1

    def describe(self) -> str:
        return f"Machine '{self._name}' (program={self._program}, cycles={self._cycles})"


class Mixer(Equipment):
    """A dough mixer."""

    def __init__(
        self,
        name: str = "Mixer",
        capacity: int = 5,
        speed: int = 3,
    ) -> None:
        super().__init__(name, capacity)
        self._speed = speed

    def describe(self) -> str:
        return f"Mixer at speed {self._speed}"


class Fridge(Equipment):
    """A refrigerator with a temperature setting."""

    def __init__(
        self,
        name: str = "Fridge",
        capacity: int = 50,
        temp_c: int = 4,
    ) -> None:
        super().__init__(name, capacity)
        self._temp_c = temp_c

    def is_safe_temp(self) -> bool:
        """Return True if the temperature is in the safe range 0-8 C."""
        return 0 <= self._temp_c <= 8

    def describe(self) -> str:
        return f"Fridge at {self._temp_c} C"


class Freezer(Equipment):
    """A freezer with a temperature setting."""

    def __init__(
        self,
        name: str = "Freezer",
        capacity: int = 50,
        temp_c: int = -18,
    ) -> None:
        super().__init__(name, capacity)
        self._temp_c = temp_c

    def is_deep_freeze(self) -> bool:
        """Return True if the temperature is -18 C or lower."""
        return self._temp_c <= -18

    def describe(self) -> str:
        return f"Freezer at {self._temp_c} C"


class Workstation(Equipment):
    """A prep workstation with a specific purpose."""

    def __init__(self, name: str, capacity: int, purpose: str) -> None:
        super().__init__(name, capacity)
        self._purpose = purpose

    def describe(self) -> str:
        return f"Workstation '{self._name}' for {self._purpose}"
