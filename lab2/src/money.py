"""Money value object for the culinary domain."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from .exceptions import InsufficientFundsError, InvalidQuantityError

CURRENCY_RUB = "RUB"
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"
_SUPPORTED_CURRENCIES = {CURRENCY_RUB, CURRENCY_USD, CURRENCY_EUR}
MINOR_UNITS_PER_MAJOR = 100


@dataclass
class Money:
    """Amount of money in a single currency.

    Stores an integer number of *minor units* (kopecks, cents) to avoid
    floating-point drift.
    """

    amount_minor: int
    currency: str = CURRENCY_RUB

    def __post_init__(self) -> None:
        if self.currency not in _SUPPORTED_CURRENCIES:
            raise InvalidQuantityError(f"Unsupported currency: {self.currency!r}")

    @classmethod
    def from_major(cls, amount: float, currency: str = CURRENCY_RUB) -> "Money":
        """Create Money from a value in the major unit (e.g. 12.34 RUB)."""
        return cls(int(amount * MINOR_UNITS_PER_MAJOR + 0.5), currency)

    def as_major(self) -> float:
        """Return the amount as a float in the major unit."""
        return self.amount_minor / MINOR_UNITS_PER_MAJOR

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount_minor + other.amount_minor, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        if other.amount_minor > self.amount_minor:
            raise InsufficientFundsError("Subtraction would yield negative money")
        return Money(self.amount_minor - other.amount_minor, self.currency)

    def __mul__(self, factor: Union[int, float]) -> "Money":
        return Money(round(self.amount_minor * factor), self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor == other.amount_minor and self.currency == other.currency

    def __hash__(self) -> int:
        return hash((self.amount_minor, self.currency))

    def __str__(self) -> str:
        return f"{self.as_major():.2f} {self.currency}"

    def __repr__(self) -> str:
        return f"Money({self.amount_minor}, {self.currency!r})"

    def is_zero(self) -> bool:
        """Return True if the amount is zero."""
        return self.amount_minor == 0

    def is_positive(self) -> bool:
        """Return True if the amount is strictly positive."""
        return self.amount_minor > 0

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise InvalidQuantityError(
                f"Cannot mix currencies: {self.currency} vs {other.currency}"
            )
