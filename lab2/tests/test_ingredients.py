"""Tests for the Ingredient hierarchy."""
from datetime import date, timedelta

import pytest

from lab2.src.allergens import Allergen, AllergenSet
from lab2.src.exceptions import InvalidQuantityError
from lab2.src.ingredients import (
    Dairy,
    Fish,
    Fruit,
    Grain,
    Ingredient,
    IngredientLot,
    Meat,
    Spice,
    Vegetable,
)
from lab2.src.money import Money
from lab2.src.units import Quantity, Unit


def _price():
    return Money.from_major(100.0)


class TestIngredient:
    def test_empty_name(self):
        with pytest.raises(InvalidQuantityError):
            Ingredient("", Unit.GRAM, _price())

    def test_price_for(self):
        ing = Ingredient("Sugar", Unit.KILOGRAM, Money.from_major(80.0))
        assert ing.price_for(Quantity(500, Unit.GRAM)) == Money.from_major(40.0)

    def test_eq_case_insensitive(self):
        a = Ingredient("Sugar", Unit.GRAM, _price())
        b = Ingredient("sugar", Unit.GRAM, _price())
        assert a == b

    def test_eq_other_type(self):
        a = Ingredient("Sugar", Unit.GRAM, _price())
        assert a.__eq__(1) is NotImplemented

    def test_hash(self):
        a = Ingredient("Sugar", Unit.GRAM, _price())
        b = Ingredient("sugar", Unit.GRAM, _price())
        assert hash(a) == hash(b)

    def test_str_and_repr(self):
        a = Ingredient("Sugar", Unit.GRAM, _price())
        assert str(a) == "Sugar"
        assert "Ingredient" in repr(a)

    def test_describe(self):
        a = Ingredient("Sugar", Unit.GRAM, _price())
        assert "Sugar" in a.describe()


class TestVegetable:
    def test_season_in_range(self):
        v = Vegetable("Tomato", Unit.KILOGRAM, _price(), 5, 9)
        assert v.is_in_season(date(2026, 7, 1))

    def test_season_out_of_range(self):
        v = Vegetable("Tomato", Unit.KILOGRAM, _price(), 5, 9)
        assert not v.is_in_season(date(2026, 12, 1))

    def test_wrapping_season(self):
        v = Vegetable("Kale", Unit.KILOGRAM, _price(), 11, 3)
        assert v.is_in_season(date(2026, 1, 1))
        assert v.is_in_season(date(2026, 12, 1))
        assert not v.is_in_season(date(2026, 6, 1))

    def test_organic_flag(self):
        v = Vegetable("Tomato", Unit.KILOGRAM, _price(), 5, 9, organic=True)
        assert v.is_organic()

    def test_describe(self):
        v = Vegetable("Tomato", Unit.KILOGRAM, _price(), 5, 9)
        assert "Tomato" in v.describe()


class TestFruit:
    def test_ripen(self):
        f = Fruit("Apple", Unit.KILOGRAM, _price(), 0.8)
        f.ripen(0.9)
        assert f.is_ripe()

    def test_ripen_clamped(self):
        f = Fruit("Apple", Unit.KILOGRAM, _price(), 0.8)
        f.ripen(2.0)
        f.ripen(2.0)
        assert f.is_ripe()   # never exceeds 1

    def test_sweetness_levels(self):
        assert Fruit("X", Unit.GRAM, _price(), 0.1).sweetness_level() == "sour"
        assert Fruit("X", Unit.GRAM, _price(), 0.5).sweetness_level() == "balanced"
        assert Fruit("X", Unit.GRAM, _price(), 0.9).sweetness_level() == "sweet"


class TestMeat:
    def test_safe_temperature(self):
        m = Meat("Beef", Unit.KILOGRAM, _price(), "beef", 63)
        assert m.is_safe_temperature(70)
        assert not m.is_safe_temperature(50)

    def test_recommended_technique(self):
        assert Meat("Beef", Unit.KILOGRAM, _price(), "beef", 63).recommended_technique() == "grill"
        assert Meat("Chicken", Unit.KILOGRAM, _price(), "chicken", 74).recommended_technique() == "roast"
        assert Meat("Tuna", Unit.KILOGRAM, _price(), "tuna", 60).recommended_technique() == "bake"


class TestFish:
    def test_bones(self):
        assert Fish("Cod", Unit.KILOGRAM, _price(), "cod").is_boneless()
        assert not Fish("Cod", Unit.KILOGRAM, _price(), "cod", bones=3).is_boneless()

    def test_mark_stale(self):
        f = Fish("Cod", Unit.KILOGRAM, _price(), "cod")
        f.mark_stale()
        assert not f.is_fresh()


class TestDairy:
    def test_low_fat(self):
        assert Dairy("Milk", Unit.LITER, _price(), 1.5).is_low_fat()
        assert not Dairy("Cream", Unit.LITER, _price(), 20.0).is_low_fat()

    def test_scaled_fat_capped(self):
        d = Dairy("Cream", Unit.LITER, _price(), 30.0)
        assert d.scaled_fat(5.0) == 100.0


class TestSpice:
    def test_heat_levels(self):
        assert Spice("Salt", Unit.GRAM, _price(), 0).heat_level() == "mild"
        assert Spice("Paprika", Unit.GRAM, _price(), 1000).heat_level() == "medium"
        assert Spice("Chili", Unit.GRAM, _price(), 10000).heat_level() == "hot"
        assert Spice("Habanero", Unit.GRAM, _price(), 100000).heat_level() == "extreme"

    def test_is_hot(self):
        assert Spice("Chili", Unit.GRAM, _price(), 5000).is_hot()
        assert not Spice("Salt", Unit.GRAM, _price(), 0).is_hot()


class TestGrain:
    def test_gluten(self):
        assert Grain("Rice", Unit.GRAM, _price(), 20, contains_gluten=False).is_gluten_free()
        assert not Grain("Wheat", Unit.GRAM, _price(), 30, contains_gluten=True).is_gluten_free()

    def test_scale_cooking_time(self):
        g = Grain("Rice", Unit.GRAM, _price(), 20, contains_gluten=False)
        assert g.scale_cooking_time(2.0) == 40


class TestIngredientLot:
    def test_expiry(self):
        ing = Ingredient("Flour", Unit.KILOGRAM, _price())
        today = date(2026, 9, 26)
        lot = IngredientLot(ing, Quantity(1, Unit.KILOGRAM), date(2026, 10, 1))
        assert not lot.is_expired(today)
        assert lot.days_until_expiry(today) == 5

    def test_expired(self):
        ing = Ingredient("Flour", Unit.KILOGRAM, _price())
        today = date(2026, 9, 26)
        lot = IngredientLot(ing, Quantity(1, Unit.KILOGRAM), date(2026, 9, 1))
        assert lot.is_expired(today)

    def test_consume(self):
        ing = Ingredient("Flour", Unit.KILOGRAM, _price())
        lot = IngredientLot(ing, Quantity(2, Unit.KILOGRAM), date(2026, 10, 1))
        lot.consume(Quantity(1, Unit.KILOGRAM))
        assert lot.quantity.amount == 1

    def test_consume_too_much(self):
        ing = Ingredient("Flour", Unit.KILOGRAM, _price())
        lot = IngredientLot(ing, Quantity(1, Unit.KILOGRAM), date(2026, 10, 1))
        with pytest.raises(InvalidQuantityError):
            lot.consume(Quantity(5, Unit.KILOGRAM))

    def test_is_empty(self):
        ing = Ingredient("Flour", Unit.KILOGRAM, _price())
        lot = IngredientLot(ing, Quantity(1, Unit.KILOGRAM), date(2026, 10, 1))
        lot.consume(Quantity(1, Unit.KILOGRAM))
        assert lot.is_empty()
