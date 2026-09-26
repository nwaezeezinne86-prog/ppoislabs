"""Tests for the Money value object."""
import pytest

from lab2.src.exceptions import InsufficientFundsError, InvalidQuantityError
from lab2.src.money import CURRENCY_EUR, CURRENCY_RUB, Money


class TestConstruction:
    def test_default_currency(self):
        assert Money(100).currency == CURRENCY_RUB

    def test_from_major(self):
        assert Money.from_major(12.34).amount_minor == 1234

    def test_from_major_rounds(self):
        assert Money.from_major(0.005).amount_minor == 1

    def test_invalid_currency(self):
        with pytest.raises(InvalidQuantityError):
            Money(100, "XYZ")


class TestArithmetic:
    def test_add(self):
        assert Money(100) + Money(50) == Money(150)

    def test_add_incompatible_currency(self):
        with pytest.raises(InvalidQuantityError):
            Money(100, CURRENCY_RUB) + Money(50, CURRENCY_EUR)

    def test_sub(self):
        assert Money(100) - Money(40) == Money(60)

    def test_sub_would_go_negative(self):
        with pytest.raises(InsufficientFundsError):
            Money(10) - Money(20)

    def test_mul_by_int(self):
        assert Money(100) * 3 == Money(300)

    def test_mul_by_float(self):
        assert Money(100) * 0.5 == Money(50)


class TestComparison:
    def test_eq_different_currency(self):
        assert Money(100, CURRENCY_RUB) != Money(100, CURRENCY_EUR)

    def test_eq_other_type(self):
        assert Money(100).__eq__(1) is NotImplemented

    def test_hash(self):
        assert hash(Money(100)) == hash(Money(100))


class TestHelpers:
    def test_as_major(self):
        assert Money(1234).as_major() == pytest.approx(12.34)

    def test_is_zero(self):
        assert Money(0).is_zero()
        assert not Money(1).is_zero()

    def test_is_positive(self):
        assert Money(1).is_positive()
        assert not Money(0).is_positive()

    def test_str(self):
        assert str(Money(1234)) == "12.34 RUB"

    def test_repr(self):
        assert "Money(1234" in repr(Money(1234))
