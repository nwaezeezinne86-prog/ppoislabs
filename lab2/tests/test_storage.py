"""Tests for storage: racks, zones, units, warehouses."""
from datetime import date

import pytest

from lab2.src.exceptions import InvalidQuantityError
from lab2.src.ingredients import Ingredient, IngredientLot
from lab2.src.money import Money
from lab2.src.storage import Rack, StorageUnit, StorageZone, Warehouse
from lab2.src.units import Quantity, Unit


def _lot(grams: float = 1000, expiry: date = date(2026, 10, 1)):
    ing = Ingredient("Flour", Unit.GRAM, Money.from_major(0.1))
    return IngredientLot(ing, Quantity(grams, Unit.GRAM), expiry)


class TestRack:
    def test_bad_shelf_count(self):
        with pytest.raises(InvalidQuantityError):
            Rack("A", 0, 100.0)

    def test_can_hold(self):
        r = Rack("A", 3, 100.0)
        assert r.can_hold(50.0)

    def test_add_and_utilization(self):
        r = Rack("A", 3, 100.0)
        r.add_weight(40.0)
        assert r.utilization() == 0.4

    def test_overload(self):
        r = Rack("A", 3, 100.0)
        r.add_weight(90.0)
        with pytest.raises(InvalidQuantityError):
            r.add_weight(20.0)

    def test_remove_weight_floor(self):
        r = Rack("A", 3, 100.0)
        r.add_weight(10.0)
        r.remove_weight(100.0)
        assert r.utilization() == 0.0

    def test_describe(self):
        assert "A" in Rack("A", 3, 100.0).describe()


class TestStorageZone:
    def test_add_remove_rack(self):
        z = StorageZone("Cold", 2)
        z.add_rack(Rack("R1", 3, 10.0))
        z.add_rack(Rack("R2", 3, 10.0))
        assert z.rack_count() == 2
        z.remove_rack("R1")
        assert z.rack_count() == 1

    def test_is_cold(self):
        assert StorageZone("C", 2).is_cold()
        assert not StorageZone("A", 20).is_cold()

    def test_find_rack(self):
        z = StorageZone("C", 2)
        z.add_rack(Rack("R1", 3, 10.0))
        assert z.find_rack("R1") is not None
        assert z.find_rack("X") is None

    def test_describe(self):
        assert "C" in StorageZone("C", 2).describe()


class TestStorageUnit:
    def test_bad_capacity(self):
        with pytest.raises(InvalidQuantityError):
            StorageUnit("U", 0)

    def test_store_and_take(self):
        u = StorageUnit("U", 100.0)
        u.store(_lot(5000))
        taken = u.take("Flour", Quantity(1000, Unit.GRAM))
        assert taken.quantity.amount == 4000

    def test_store_full(self):
        u = StorageUnit("U", 1.0)   # 1 kg capacity
        u.store(_lot(500))          # 0.5 kg stored
        with pytest.raises(InvalidQuantityError):
            u.store(_lot(2000))     # would be over 1 kg

    def test_take_missing(self):
        with pytest.raises(InvalidQuantityError):
            StorageUnit("U", 10.0).take("X", Quantity(1, Unit.GRAM))

    def test_utilization(self):
        u = StorageUnit("U", 2.0)
        u.store(_lot(1000))
        assert u.utilization() == pytest.approx(0.5)

    def test_expired_lots_and_purge(self):
        u = StorageUnit("U", 10.0)
        u.store(_lot(1000, expiry=date(2026, 1, 1)))
        today = date(2026, 9, 26)
        assert len(u.expired_lots(today)) == 1
        assert u.purge_expired(today) == 1
        assert u.lot_count() == 0

    def test_describe(self):
        assert "U" in StorageUnit("U", 10.0).describe()


class TestWarehouse:
    def test_add_remove_zone(self):
        w = Warehouse("Main", "Minsk")
        w.add_zone(StorageZone("Cold", 2))
        w.add_zone(StorageZone("Ambient", 20))
        assert w.zone_count() == 2
        w.remove_zone("Cold")
        assert w.zone_count() == 1

    def test_total_racks_and_cold(self):
        w = Warehouse("Main", "Minsk")
        cold = StorageZone("Cold", 2)
        cold.add_rack(Rack("R1", 3, 10.0))
        w.add_zone(cold)
        assert w.total_racks() == 1
        assert len(w.cold_zones()) == 1

    def test_find_zone(self):
        w = Warehouse("Main", "Minsk")
        w.add_zone(StorageZone("Cold", 2))
        assert w.find_zone("Cold") is not None
        assert w.find_zone("X") is None

    def test_describe(self):
        assert "Main" in Warehouse("Main", "Minsk").describe()
