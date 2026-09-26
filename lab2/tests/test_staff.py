"""Tests for staff management."""
from datetime import date, time

import pytest

from lab2.src.exceptions import InvalidScheduleError
from lab2.src.money import Money
from lab2.src.people import Cook, Waiter
from lab2.src.staff import Salary, Schedule, Shift, Staff, Team


def _cook():
    return Cook("Anna", "Ivanova", date(1995, 5, 5), date(2024, 1, 1),
                Money.from_major(4000), "pastry")


def _waiter():
    return Waiter("Boris", "Petrov", date(1998, 6, 6), date(2024, 2, 1),
                  Money.from_major(3000), "A")


class TestShift:
    def test_start_after_end(self):
        with pytest.raises(InvalidScheduleError):
            Shift(_cook(), date(2026, 9, 28), time(17, 0), time(9, 0))

    def test_hours(self):
        s = Shift(_cook(), date(2026, 9, 28), time(9, 0), time(17, 0))
        assert s.hours() == 8.0

    def test_overlaps(self):
        cook = _cook()
        a = Shift(cook, date(2026, 9, 28), time(9, 0), time(13, 0))
        b = Shift(cook, date(2026, 9, 28), time(12, 0), time(16, 0))
        assert a.overlaps(b)

    def test_no_overlap_different_day(self):
        cook = _cook()
        a = Shift(cook, date(2026, 9, 28), time(9, 0), time(13, 0))
        b = Shift(cook, date(2026, 9, 29), time(9, 0), time(13, 0))
        assert not a.overlaps(b)

    def test_no_overlap_same_day(self):
        cook = _cook()
        a = Shift(cook, date(2026, 9, 28), time(9, 0), time(13, 0))
        b = Shift(cook, date(2026, 9, 28), time(13, 0), time(17, 0))
        assert not a.overlaps(b)

    def test_describe(self):
        s = Shift(_cook(), date(2026, 9, 28), time(9, 0), time(17, 0))
        assert "Anna" in s.describe()


class TestSchedule:
    def test_add_shift(self):
        sched = Schedule(date(2026, 9, 28))
        sched.add_shift(Shift(_cook(), date(2026, 9, 28), time(9, 0), time(17, 0)))
        assert sched.shift_count() == 1

    def test_overlap_raises(self):
        sched = Schedule(date(2026, 9, 28))
        cook = _cook()
        sched.add_shift(Shift(cook, date(2026, 9, 28), time(9, 0), time(13, 0)))
        with pytest.raises(InvalidScheduleError):
            sched.add_shift(Shift(cook, date(2026, 9, 28), time(12, 0), time(16, 0)))

    def test_remove_shift(self):
        sched = Schedule(date(2026, 9, 28))
        s = Shift(_cook(), date(2026, 9, 28), time(9, 0), time(17, 0))
        sched.add_shift(s)
        sched.remove_shift(s)
        assert sched.shift_count() == 0

    def test_hours_for(self):
        cook = _cook()
        sched = Schedule(date(2026, 9, 28))
        sched.add_shift(Shift(cook, date(2026, 9, 28), time(9, 0), time(17, 0)))
        sched.add_shift(Shift(cook, date(2026, 9, 29), time(9, 0), time(17, 0)))
        assert sched.hours_for(cook) == 16.0

    def test_total_hours(self):
        sched = Schedule(date(2026, 9, 28))
        sched.add_shift(Shift(_cook(), date(2026, 9, 28), time(9, 0), time(17, 0)))
        assert sched.total_hours() == 8.0

    def test_shifts_for(self):
        cook = _cook()
        sched = Schedule(date(2026, 9, 28))
        sched.add_shift(Shift(cook, date(2026, 9, 28), time(9, 0), time(17, 0)))
        assert len(sched.shifts_for(cook)) == 1

    def test_describe(self):
        assert "Schedule" in Schedule(date(2026, 9, 28)).describe()


class TestSalary:
    def test_net(self):
        s = Salary(_cook(), "2026-09", Money.from_major(4000))
        s.add_bonus(Money.from_major(500))
        s.add_deduction(Money.from_major(200))
        assert s.net() == Money.from_major(4300)

    def test_bonus_total_empty(self):
        assert Salary(_cook(), "2026-09", Money.from_major(4000)).bonus_total().is_zero()

    def test_bonus_total(self):
        s = Salary(_cook(), "2026-09", Money.from_major(4000))
        s.add_bonus(Money.from_major(100))
        s.add_bonus(Money.from_major(200))
        assert s.bonus_total() == Money.from_major(300)

    def test_describe(self):
        s = Salary(_cook(), "2026-09", Money.from_major(4000))
        assert "2026-09" in s.describe()


class TestStaff:
    def test_hire_and_count(self):
        roster = Staff("K")
        roster.hire(_cook())
        roster.hire(_waiter())
        assert roster.active_count() == 2

    def test_fire(self):
        roster = Staff("K")
        cook = _cook()
        roster.hire(cook)
        roster.fire(cook)
        assert roster.active_count() == 0

    def test_total_payroll(self):
        roster = Staff("K")
        roster.hire(_cook())
        roster.hire(_waiter())
        assert roster.total_payroll() == Money.from_major(7000)

    def test_total_payroll_empty(self):
        assert Staff("K").total_payroll().is_zero()

    def test_find_by_name(self):
        roster = Staff("K")
        roster.hire(_cook())
        assert roster.find_by_name("Anna Ivanova") is not None

    def test_find_missing(self):
        assert Staff("K").find_by_name("X") is None

    def test_describe(self):
        roster = Staff("K")
        roster.hire(_cook())
        assert "K" in roster.describe()


class TestTeam:
    def test_size(self):
        t = Team("X", _cook())
        assert t.size() == 1

    def test_add_member(self):
        cook = _cook()
        t = Team("X", cook)
        t.add_member(_waiter())
        t.add_member(cook)   # duplicate
        assert t.size() == 2

    def test_remove_member(self):
        cook = _cook()
        waiter = _waiter()
        t = Team("X", cook)
        t.add_member(waiter)
        t.remove_member(waiter)
        assert t.size() == 1

    def test_remove_leader_raises(self):
        cook = _cook()
        t = Team("X", cook)
        with pytest.raises(InvalidScheduleError):
            t.remove_member(cook)

    def test_members_copy(self):
        t = Team("X", _cook())
        members = t.members()
        members.append(_waiter())
        assert t.size() == 1

    def test_describe(self):
        assert "X" in Team("X", _cook()).describe()
