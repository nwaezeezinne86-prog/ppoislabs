"""Tests for kitchen equipment."""
import pytest

from lab2.src.equipment import (
    Blender,
    Equipment,
    Freezer,
    Fridge,
    Machine,
    Mixer,
    Oven,
    Stove,
    Workstation,
)
from lab2.src.exceptions import EquipmentBrokenError, EquipmentUnavailableError


class TestBase:
    def test_capacity_positive(self):
        with pytest.raises(ValueError):
            Oven(capacity=0)

    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            Equipment("x", 1)

    def test_acquire_release(self):
        o = Oven()
        o.acquire()
        assert not o.is_available()
        assert o.uses() == 1
        o.release()
        assert o.is_available()

    def test_acquire_twice(self):
        o = Oven()
        o.acquire()
        with pytest.raises(EquipmentUnavailableError):
            o.acquire()

    def test_broken_blocks_acquire(self):
        o = Oven()
        o.mark_broken()
        with pytest.raises(EquipmentBrokenError):
            o.acquire()

    def test_repair(self):
        o = Oven()
        o.mark_broken()
        o.repair()
        assert o.is_available()

    def test_str_and_repr(self):
        o = Oven()
        assert str(o) == "Oven"
        assert "Oven" in repr(o)


class TestOven:
    def test_temp_allowed(self):
        o = Oven(max_temp_c=250)
        assert o.is_temp_allowed(200)
        assert not o.is_temp_allowed(300)
        assert not o.is_temp_allowed(0)

    def test_describe(self):
        assert "Oven" in Oven().describe()


class TestStove:
    def test_burner_limits(self):
        s = Stove(burners=2)
        s.light_burner()
        s.light_burner()
        with pytest.raises(EquipmentUnavailableError):
            s.light_burner()

    def test_extinguish(self):
        s = Stove(burners=2)
        s.light_burner()
        s.extinguish_burner()
        s.light_burner()  # doesn't raise


class TestBlenderMixer:
    def test_describe(self):
        assert "Blender" in Blender().describe()
        assert "Mixer" in Mixer().describe()


class TestMachine:
    def test_run_cycle_requires_acquire(self):
        m = Machine("Slicer", 1, "thin")
        with pytest.raises(EquipmentUnavailableError):
            m.run_cycle()

    def test_run_cycle(self):
        m = Machine("Slicer", 1, "thin")
        m.acquire()
        m.run_cycle()
        m.run_cycle()
        assert "cycles=2" in m.describe()


class TestFridgeFreezer:
    def test_fridge_safe_temp(self):
        assert Fridge(temp_c=4).is_safe_temp()
        assert not Fridge(temp_c=20).is_safe_temp()

    def test_freezer_deep_freeze(self):
        assert Freezer(temp_c=-20).is_deep_freeze()
        assert not Freezer(temp_c=-10).is_deep_freeze()


class TestWorkstation:
    def test_describe(self):
        ws = Workstation("Prep-1", 1, "chopping")
        assert "Prep-1" in ws.describe()
        assert "chopping" in ws.describe()
