"""Business entities: restaurants, branches, tables, reservations, reviews."""
from __future__ import annotations

from datetime import date, time

from .exceptions import (
    ReservationConflictError,
    TableNotFoundError,
)


class Table:
    """A physical table in a restaurant."""

    def __init__(self, number: int, seats: int, location: str = "indoor") -> None:
        if number <= 0:
            raise ValueError("Table number must be positive")
        if seats <= 0:
            raise ValueError("Table seats must be positive")
        self._number = number
        self._seats = seats
        self._location = location

    @property
    def number(self) -> int:
        """Table number."""
        return self._number

    @property
    def seats(self) -> int:
        """Number of seats."""
        return self._seats

    def can_host(self, guests: int) -> bool:
        """Return True if the table can seat the given number of guests."""
        return 0 < guests <= self._seats

    def describe(self) -> str:
        return f"Table #{self._number} ({self._seats} seats, {self._location})"


class Reservation:
    """A table reservation for a given date and time."""

    def __init__(
        self,
        customer_name: str,
        table: Table,
        day: date,
        start: time,
        hours: int,
    ) -> None:
        if hours <= 0:
            raise ValueError("Reservation duration must be positive")
        if not table.can_host(1):
            raise ReservationConflictError("Table cannot host any guests")
        self._customer_name = customer_name
        self._table = table
        self._day = day
        self._start = start
        self._hours = hours
        self._cancelled = False

    @property
    def customer_name(self) -> str:
        """Customer name."""
        return self._customer_name

    @property
    def table(self) -> Table:
        """Reserved table."""
        return self._table

    @property
    def day(self) -> date:
        """Reservation date."""
        return self._day

    def end_time_minutes(self) -> int:
        """Return end time as minutes since midnight."""
        return self._start.hour * 60 + self._start.minute + self._hours * 60

    def overlaps(self, other: "Reservation") -> bool:
        """Return True if two reservations overlap on the same table/day."""
        if self._day != other._day or self._table != other._table:
            return False
        start_a = self._start.hour * 60 + self._start.minute
        start_b = other._start.hour * 60 + other._start.minute
        return not (
            self.end_time_minutes() <= start_b
            or other.end_time_minutes() <= start_a
        )

    def cancel(self) -> None:
        """Cancel the reservation."""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Return True if the reservation was cancelled."""
        return self._cancelled

    def describe(self) -> str:
        status = "cancelled" if self._cancelled else "active"
        return (
            f"Reservation for {self._customer_name} at {self._table.describe()} "
            f"on {self._day} {self._start:%H:%M} for {self._hours}h [{status}]"
        )


class Review:
    """A customer review with a rating and text."""

    def __init__(self, author: str, rating: int, text: str) -> None:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self._author = author
        self._rating = rating
        self._text = text
        self._helpful_votes = 0

    @property
    def author(self) -> str:
        """Review author."""
        return self._author

    @property
    def rating(self) -> int:
        """Rating from 1 to 5."""
        return self._rating

    def vote_helpful(self) -> None:
        """Register a helpful vote."""
        self._helpful_votes += 1

    def helpful_votes(self) -> int:
        """Return the number of helpful votes."""
        return self._helpful_votes

    def is_positive(self) -> bool:
        """Return True if the rating is 4 or 5."""
        return self._rating >= 4

    def describe(self) -> str:
        return f"{self._author} rated {self._rating}/5: {self._text}"


class Promotion:
    """A discount promotion available in a restaurant."""

    def __init__(self, name: str, discount_percent: float) -> None:
        if not 0 < discount_percent <= 100:
            raise ValueError("Discount must be between 0 and 100")
        self._name = name
        self._discount_percent = discount_percent
        self._active = True

    @property
    def name(self) -> str:
        """Promotion name."""
        return self._name

    @property
    def discount_percent(self) -> float:
        """Discount percent."""
        return self._discount_percent

    def is_active(self) -> bool:
        """Return True while the promotion is active."""
        return self._active

    def deactivate(self) -> None:
        """Deactivate the promotion."""
        self._active = False

    def apply_to(self, amount_minor: int) -> int:
        """Return the discounted amount in minor units."""
        factor = (100.0 - self._discount_percent) / 100.0
        return round(amount_minor * factor)

    def describe(self) -> str:
        status = "active" if self._active else "inactive"
        return f"Promotion {self._name} (-{self._discount_percent}%) [{status}]"


class Branch:
    """A branch of a restaurant chain."""

    def __init__(self, name: str, address: str, seats: int) -> None:
        if seats <= 0:
            raise ValueError("Branch seats must be positive")
        self._name = name
        self._address = address
        self._seats = seats
        self._tables: list[Table] = []
        self._reservations: list[Reservation] = []
        self._reviews: list[Review] = []

    @property
    def name(self) -> str:
        """Branch name."""
        return self._name

    def add_table(self, table: Table) -> None:
        """Add a table to the branch."""
        self._tables.append(table)

    def find_table(self, number: int) -> Table:
        """Return a table by number or raise TableNotFoundError."""
        for t in self._tables:
            if t.number == number:
                return t
        raise TableNotFoundError(f"Table #{number} not found")

    def reserve(
        self,
        customer_name: str,
        table_number: int,
        day: date,
        start: time,
        hours: int,
    ) -> Reservation:
        """Reserve a table, raising on conflict."""
        table = self.find_table(table_number)
        new = Reservation(customer_name, table, day, start, hours)
        for existing in self._reservations:
            if existing.is_cancelled():
                continue
            if existing.overlaps(new):
                raise ReservationConflictError(
                    f"Conflict with {existing.describe()}"
                )
        self._reservations.append(new)
        return new

    def add_review(self, review: Review) -> None:
        """Add a review for the branch."""
        self._reviews.append(review)

    def average_rating(self) -> float:
        """Return the average rating, 0 if there are no reviews."""
        if not self._reviews:
            return 0.0
        total = sum(r.rating for r in self._reviews)
        return total / len(self._reviews)

    def table_count(self) -> int:
        """Return the number of tables."""
        return len(self._tables)

    def reservation_count(self) -> int:
        """Return the number of reservations (cancelled included)."""
        return len(self._reservations)

    def describe(self) -> str:
        return (
            f"Branch '{self._name}' at {self._address} "
            f"({self.table_count()} tables, {self._seats} seats, "
            f"avg rating {self.average_rating():.2f})"
        )


class Restaurant:
    """The top-level restaurant with branches and promotions."""

    def __init__(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Restaurant name must not be empty")
        self._name = name
        self._branches: list[Branch] = []
        self._promotions: list[Promotion] = []

    @property
    def name(self) -> str:
        """Restaurant name."""
        return self._name

    def add_branch(self, branch: Branch) -> None:
        """Add a branch."""
        self._branches.append(branch)

    def remove_branch(self, name: str) -> None:
        """Remove a branch by name."""
        self._branches = [b for b in self._branches if b.name != name]

    def find_branch(self, name: str) -> Branch | None:
        """Return a branch by name or None."""
        for b in self._branches:
            if b.name == name:
                return b
        return None

    def add_promotion(self, promotion: Promotion) -> None:
        """Add a promotion."""
        self._promotions.append(promotion)

    def active_promotions(self) -> list[Promotion]:
        """Return only active promotions."""
        return [p for p in self._promotions if p.is_active()]

    def branch_count(self) -> int:
        """Return the number of branches."""
        return len(self._branches)

    def total_tables(self) -> int:
        """Return the total number of tables across branches."""
        return sum(b.table_count() for b in self._branches)

    def overall_rating(self) -> float:
        """Return the average rating across all branches."""
        if not self._branches:
            return 0.0
        ratings = [b.average_rating() for b in self._branches if b.average_rating() > 0]
        if not ratings:
            return 0.0
        return sum(ratings) / len(ratings)

    def describe(self) -> str:
        return (
            f"Restaurant '{self._name}' "
            f"({self.branch_count()} branches, "
            f"{self.total_tables()} tables, "
            f"{len(self.active_promotions())} active promotions)"
        )
