"""Tests for units and Quantity."""
import pytest

from lab2.src.exceptions import InvalidQuantityError, InvalidUnitError
from lab2.src.units import (
    Quantity,
    Unit,
    convert,
    is_count,
    is_mass,
    is_volume,
    normalize_to_base,
)


class TestUnitClassification:
    def test_mass(self):
        assert is_mass(Unit.GRAM)
        assert is_mass(Unit.KILOGRAM)
        assert not is_mass(Unit.LITER)

    def test_volume(self):
        assert is_volume(Unit.MILLILITER)
        assert is_volume(Unit.CUP)
        assert not is_volume(Unit.GRAM)

    def test_count(self):
        assert is_count(Unit.PIECE)
        assert not is_count(Unit.GRAM)


class TestConvert:
    def test_same_unit(self):
        assert convert(5, Unit.GRAM, Unit.GRAM) == 5

    def test_kg_to_g(self):
        assert convert(1, Unit.KILOGRAM, Unit.GRAM) == 1000

    def test_g_to_kg(self):
        assert convert(500, Unit.GRAM, Unit.KILOGRAM) == pytest.approx(0.5)

    def test_liter_to_ml(self):
        assert convert(1, Unit.LITER, Unit.MILLILITER) == 1000

    def test_tsp_to_ml(self):
        assert convert(2, Unit.TEASPOON, Unit.MILLILITER) == 10

    def test_negative_amount(self):
        with pytest.raises(InvalidQuantityError):
            convert(-1, Unit.GRAM, Unit.KILOGRAM)

    def test_incompatible_dimensions(self):
        with pytest.raises(InvalidUnitError):
            convert(1, Unit.GRAM, Unit.MILLILITER)

    def test_piece_to_piece(self):
        assert convert(3, Unit.PIECE, Unit.PIECE) == 3


class TestNormalize:
    def test_mass(self):
        assert normalize_to_base(2, Unit.KILOGRAM) == (2000, "g")

    def test_volume(self):
        assert normalize_to_base(0.5, Unit.LITER) == (500, "ml")

    def test_count(self):
        assert normalize_to_base(3, Unit.PIECE) == (3, "pc")


class TestQuantity:
    def test_negative_raises(self):
        with pytest.raises(InvalidQuantityError):
            Quantity(-1, Unit.GRAM)

    def test_to(self):
        q = Quantity(1, Unit.KILOGRAM)
        assert q.to(Unit.GRAM).amount == 1000

    def test_eq_across_units(self):
        assert Quantity(1000, Unit.GRAM) == Quantity(1, Unit.KILOGRAM)

    def test_eq_incompatible(self):
        assert Quantity(1, Unit.GRAM) != Quantity(1, Unit.LITER)

    def test_hash(self):
        assert hash(Quantity(1, Unit.GRAM)) == hash(Quantity(1, Unit.GRAM))

    def test_add(self):
        result = Quantity(200, Unit.GRAM) + Quantity(1, Unit.KILOGRAM)
        assert result.amount == 1200

    def test_mul(self):
        assert (Quantity(100, Unit.GRAM) * 3).amount == 300

    def test_is_zero(self):
        assert Quantity(0, Unit.GRAM).is_zero()
        assert not Quantity(1, Unit.GRAM).is_zero()

    def test_str(self):
        assert str(Quantity(500, Unit.GRAM)) == "500 g"
