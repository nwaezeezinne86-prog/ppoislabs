"""Tests for the kitchen: tasks, stations, kitchen, handovers."""
from datetime import date, datetime, timedelta

import pytest

from lab2.src.equipment import Oven
from lab2.src.exceptions import (
    EquipmentUnavailableError,
    InvalidScheduleError,
)
from lab2.src.kitchen import Kitchen, KitchenTask, ShiftHandover, Workstation
from lab2.src.money import Money
from lab2.src.people import Cook


def _cook(name: str = "Anna"):
    return Cook(name, "Ivanova", date(1995, 5, 5), date(2024, 1, 1),
                Money.from_major(4000), "pastry")


def _cook2():
    return Cook("Boris", "Petrov", date(1998, 6, 6), date(2024, 2, 1),
                Money.from_major(3500), "grill")


class TestKitchenTask:
    def test_bad_minutes(self):
        with pytest.raises(InvalidScheduleError):
            KitchenTask("X", 0)

    def test_full_lifecycle(self):
        t = KitchenTask("Bake", 30, _cook())
        assert t.status == KitchenTask.STATUS_PENDING
        now = datetime(2026, 9, 26, 9, 0)
        t.start(now)
        assert t.status == KitchenTask.STATUS_RUNNING
        t.finish(now + timedelta(minutes=30))
        assert t.status == KitchenTask.STATUS_DONE
        assert t.actual_duration() == timedelta(minutes=30)

    def test_start_twice(self):
        t = KitchenTask("Bake", 30)
        t.start(datetime(2026, 9, 26, 9, 0))
        with pytest.raises(InvalidScheduleError):
            t.start(datetime(2026, 9, 26, 9, 30))

    def test_finish_without_start(self):
        with pytest.raises(InvalidScheduleError):
            KitchenTask("Bake", 30).finish(datetime(2026, 9, 26, 9, 30))

    def test_fail_marks_status(self):
        t = KitchenTask("Bake", 30)
        t.fail("burnt")
        assert t.status == KitchenTask.STATUS_FAILED
        assert "burnt" in t.name

    def test_actual_duration_none(self):
        assert KitchenTask("X", 30).actual_duration() is None

    def test_describe(self):
        t = KitchenTask("Bake", 30, _cook())
        assert "Bake" in t.describe()


class TestWorkstation:
    def test_assign_and_describe(self):
        ws = Workstation("P1", "baking", Oven())
        ws.assign_cook(_cook())
        assert "Anna" in ws.describe()

    def test_queue_and_pop(self):
        ws = Workstation("P1", "baking")
        ws.queue_task(KitchenTask("A", 10))
        ws.queue_task(KitchenTask("B", 20))
        assert ws.task_count() == 2
        assert ws.pending_count() == 2
        next_task = ws.pop_next()
        assert next_task.name == "A"

    def test_pop_returns_none_when_done(self):
        ws = Workstation("P1", "baking")
        assert ws.pop_next() is None

    def test_unassign(self):
        ws = Workstation("P1", "baking")
        ws.assign_cook(_cook())
        ws.unassign_cook()
        assert "unassigned" in ws.describe()

    def test_acquire_release_equipment(self):
        oven = Oven()
        ws = Workstation("P1", "baking", oven)
        ws.acquire_equipment()
        ws.release_equipment()
        assert oven.is_available()

    def test_no_equipment(self):
        ws = Workstation("P1", "baking")
        with pytest.raises(EquipmentUnavailableError):
            ws.acquire_equipment()


class TestKitchen:
    def test_add_find_remove(self):
        k = Kitchen("Main")
        ws = Workstation("P1", "baking")
        k.add_station(ws)
        assert k.find_station("P1") is ws
        assert k.find_station("X") is None
        k.remove_station("P1")
        assert k.station_count() == 0

    def test_pending_tasks(self):
        k = Kitchen("Main")
        ws = Workstation("P1", "baking")
        ws.queue_task(KitchenTask("A", 10))
        ws.queue_task(KitchenTask("B", 20))
        k.add_station(ws)
        assert k.total_pending_tasks() == 2
        assert len(k.all_tasks()) == 2
        assert k.find_task("A") is not None
        assert k.find_task("Z") is None

    def test_describe(self):
        k = Kitchen("Main")
        k.add_station(Workstation("P1", "baking"))
        assert "Main" in k.describe()


class TestShiftHandover:
    def test_same_cook(self):
        with pytest.raises(InvalidScheduleError):
            ShiftHandover(Kitchen("Main"), _cook(), _cook(),
                          datetime(2026, 9, 26, 9, 0))

    def test_notes_and_describe(self):
        k = Kitchen("Main")
        h = ShiftHandover(k, _cook(), _cook2(), datetime(2026, 9, 26, 9, 0))
        h.add_note("x")
        h.add_note("y")
        assert h.note_count() == 2
        assert "Anna" in h.describe()
