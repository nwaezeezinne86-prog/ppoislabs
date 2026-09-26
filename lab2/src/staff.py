"""Staff management: shifts, schedules, teams."""
from __future__ import annotations

from datetime import date, time

from .exceptions import InvalidScheduleError
from .money import Money
from .people import Employee


class Shift:
    """A single shift: start time, end time, and assigned employee."""

    def __init__(
        self,
        employee: Employee,
        day: date,
        start: time,
        end: time,
    ) -> None:
        if start >= end:
            raise InvalidScheduleError("Shift start must be before end")
        self._employee = employee
        self._day = day
        self._start = start
        self._end = end

    @property
    def employee(self) -> Employee:
        """Employee assigned to this shift."""
        return self._employee

    @property
    def day(self) -> date:
        """Calendar day."""
        return self._day

    def hours(self) -> float:
        """Return shift length in hours."""
        start_minutes = self._start.hour * 60 + self._start.minute
        end_minutes = self._end.hour * 60 + self._end.minute
        return (end_minutes - start_minutes) / 60.0

    def overlaps(self, other: "Shift") -> bool:
        """Return True if the two shifts overlap on the same day and employee."""
        if self._day != other._day or self._employee != other._employee:
            return False
        return not (self._end <= other._start or other._end <= self._start)

    def describe(self) -> str:
        """Return a one-line description."""
        return (
            f"{self._employee.full_name()} {self._day} "
            f"{self._start:%H:%M}-{self._end:%H:%M}"
        )


class Schedule:
    """A weekly schedule of shifts for a set of employees."""

    def __init__(self, week_start: date) -> None:
        self._week_start = week_start
        self._shifts: list[Shift] = []

    @property
    def week_start(self) -> date:
        """Monday of the scheduled week."""
        return self._week_start

    def add_shift(self, shift: Shift) -> None:
        """Add a shift; raise on overlap with an existing one."""
        for existing in self._shifts:
            if existing.overlaps(shift):
                raise InvalidScheduleError(
                    f"Overlap: {existing.describe()} vs {shift.describe()}"
                )
        self._shifts.append(shift)

    def remove_shift(self, shift: Shift) -> None:
        """Remove a shift."""
        if shift in self._shifts:
            self._shifts.remove(shift)

    def shifts_for(self, employee: Employee) -> list[Shift]:
        """Return all shifts assigned to a given employee."""
        return [s for s in self._shifts if s.employee == employee]

    def total_hours(self) -> float:
        """Return the total number of scheduled hours."""
        return sum(s.hours() for s in self._shifts)

    def hours_for(self, employee: Employee) -> float:
        """Return the total hours for one employee."""
        return sum(s.hours() for s in self.shifts_for(employee))

    def shift_count(self) -> int:
        """Return the total number of shifts."""
        return len(self._shifts)

    def describe(self) -> str:
        """Return a multi-line description."""
        lines = [f"Schedule for week of {self._week_start}:"]
        for s in self._shifts:
            lines.append(f"  {s.describe()}")
        return "\n".join(lines)


class Salary:
    """A monthly salary record: base + bonuses - deductions."""

    def __init__(self, employee: Employee, month: str, base: Money) -> None:
        self._employee = employee
        self._month = month
        self._base = base
        self._bonuses: list[Money] = []
        self._deductions: list[Money] = []

    def add_bonus(self, amount: Money) -> None:
        """Add a bonus."""
        self._bonuses.append(amount)

    def add_deduction(self, amount: Money) -> None:
        """Add a deduction."""
        self._deductions.append(amount)

    def net(self) -> Money:
        """Return base + bonuses - deductions."""
        total = self._base
        for bonus in self._bonuses:
            total = total + bonus
        for ded in self._deductions:
            total = total - ded
        return total

    def bonus_total(self) -> Money:
        """Return the sum of bonuses."""
        if not self._bonuses:
            return Money(0)
        total = self._bonuses[0]
        for b in self._bonuses[1:]:
            total = total + b
        return total

    def describe(self) -> str:
        """Return a one-line description."""
        return f"{self._employee.full_name()} {self._month}: net {self.net()}"


class Staff:
    """A roster of employees."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._employees: list[Employee] = []

    @property
    def name(self) -> str:
        """Staff group name."""
        return self._name

    def hire(self, employee: Employee) -> None:
        """Add an employee to the roster."""
        self._employees.append(employee)

    def fire(self, employee: Employee) -> None:
        """Terminate and remove an employee."""
        if employee in self._employees:
            employee.terminate()
            self._employees.remove(employee)

    def active_count(self) -> int:
        """Return the number of active employees."""
        return sum(1 for e in self._employees if e.is_active())

    def total_payroll(self) -> Money:
        """Return the sum of all active salaries."""
        active = [e for e in self._employees if e.is_active()]
        if not active:
            return Money(0)
        total = active[0].salary
        for e in active[1:]:
            total = total + e.salary
        return total

    def find_by_name(self, full_name: str) -> Employee | None:
        """Return the first employee with a matching name, or None."""
        for e in self._employees:
            if e.full_name() == full_name:
                return e
        return None

    def describe(self) -> str:
        """Return a multi-line description."""
        lines = [f"Staff '{self._name}' ({self.active_count()} active):"]
        for e in self._employees:
            status = "active" if e.is_active() else "inactive"
            lines.append(f"  {e.full_name()} [{status}]")
        return "\n".join(lines)


class Team:
    """A named team of employees with a leader."""

    def __init__(self, name: str, leader: Employee) -> None:
        self._name = name
        self._leader = leader
        self._members: list[Employee] = [leader]

    @property
    def name(self) -> str:
        """Team name."""
        return self._name

    @property
    def leader(self) -> Employee:
        """Team leader."""
        return self._leader

    def add_member(self, employee: Employee) -> None:
        """Add a member if not already present."""
        if employee not in self._members:
            self._members.append(employee)

    def remove_member(self, employee: Employee) -> None:
        """Remove a member (except the leader)."""
        if employee == self._leader:
            raise InvalidScheduleError("Cannot remove the leader from the team")
        if employee in self._members:
            self._members.remove(employee)

    def size(self) -> int:
        """Return the team size."""
        return len(self._members)

    def members(self) -> list[Employee]:
        """Return a copy of the members list."""
        return list(self._members)

    def describe(self) -> str:
        return (
            f"Team '{self._name}' (leader {self._leader.full_name()}, "
            f"{self.size()} members)"
        )
