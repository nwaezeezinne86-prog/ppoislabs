"""Tests for the BigInt class."""
import pytest

from lab1.src.big_int import BigInt


class TestConstruction:
    def test_default(self):
        assert str(BigInt()) == "0"

    def test_from_int_positive(self):
        assert str(BigInt(12345)) == "12345"

    def test_from_int_negative(self):
        assert str(BigInt(-987)) == "-987"

    def test_from_str_positive_sign(self):
        assert str(BigInt("+42")) == "42"

    def test_from_str_negative(self):
        assert str(BigInt("-00123")) == "-123"

    def test_from_str_invalid(self):
        with pytest.raises(ValueError):
            BigInt("12a3")

    def test_from_str_empty(self):
        with pytest.raises(ValueError):
            BigInt("   ")

    def test_from_str_only_sign(self):
        with pytest.raises(ValueError):
            BigInt("-")

    def test_from_bigint_copy(self):
        a = BigInt("99999999999999999999")
        b = BigInt(a)
        assert a == b
        b += BigInt(1)
        assert a != b

    def test_unsupported_type(self):
        with pytest.raises(TypeError):
            BigInt(3.14)

    def test_properties(self):
        assert BigInt(-5).sign == -1
        assert BigInt(0).sign == 0
        assert BigInt(0).is_zero
        assert not BigInt(1).is_zero


class TestComparison:
    def test_eq_int(self):
        assert BigInt(5) == 5

    def test_eq_other_type(self):
        assert BigInt(5).__eq__("x") is NotImplemented

    def test_ne(self):
        assert BigInt(5) != BigInt(6)

    def test_hash(self):
        assert hash(BigInt(42)) == hash(BigInt(42))

    def test_lt(self):
        assert BigInt(-10) < BigInt(3)
        assert BigInt(-3) < BigInt(-1)
        assert BigInt(1) < BigInt(10)
        assert not (BigInt(5) < BigInt(5))

    def test_le_gt_ge(self):
        a, b = BigInt(5), BigInt(7)
        assert a <= b and a < b
        assert b >= a and b > a
        assert a <= BigInt(5) and a >= BigInt(5)


class TestArithmetic:
    @pytest.mark.parametrize(
        "a,b,expected",
        [
            ("0", "0", "0"),
            ("1", "2", "3"),
            ("-1", "-2", "-3"),
            ("5", "-3", "2"),
            ("3", "-5", "-2"),
            ("99999999999999999999", "1", "100000000000000000000"),
            ("100000000000000000000", "-1", "99999999999999999999"),
        ],
    )
    def test_add(self, a, b, expected):
        assert str(BigInt(a) + BigInt(b)) == expected

    def test_add_int(self):
        assert BigInt(5) + 7 == BigInt(12)

    def test_sub(self):
        assert BigInt(10) - BigInt(3) == BigInt(7)
        assert BigInt(3) - BigInt(10) == BigInt(-7)
        assert BigInt(10) - 3 == BigInt(7)

    def test_mul(self):
        assert BigInt(12) * BigInt(12) == BigInt(144)
        assert BigInt(-3) * BigInt(4) == BigInt(-12)
        assert BigInt(0) * BigInt("99999999999") == BigInt(0)
        assert BigInt(7) * 6 == BigInt(42)

    def test_div(self):
        assert BigInt(144) // BigInt(12) == BigInt(12)
        assert BigInt(-144) // BigInt(12) == BigInt(-12)
        assert BigInt(7) // 2 == BigInt(3)
        assert BigInt(7) / 2 == BigInt(3)

    def test_div_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            BigInt(1) // BigInt(0)

    def test_mod(self):
        assert BigInt(7) % BigInt(3) == BigInt(1)
        assert BigInt(-7) % BigInt(3) == BigInt(-1)
        with pytest.raises(ZeroDivisionError):
            BigInt(1) % BigInt(0)

    def test_compound_ops(self):
        a = BigInt(10)
        a += BigInt(5)
        assert a == BigInt(15)
        a -= BigInt(3)
        assert a == BigInt(12)
        a *= BigInt(2)
        assert a == BigInt(24)
        a //= BigInt(4)
        assert a == BigInt(6)

    def test_unary_neg(self):
        assert -BigInt(5) == BigInt(-5)


class TestIncrementDecrement:
    def test_post_increment(self):
        a = BigInt(5)
        old = a.increment()
        assert old == BigInt(5)
        assert a == BigInt(6)

    def test_post_decrement(self):
        a = BigInt(5)
        old = a.decrement()
        assert old == BigInt(5)
        assert a == BigInt(4)

    def test_pre_increment(self):
        a = BigInt(5)
        assert a.pre_increment() is a
        assert a == BigInt(6)

    def test_pre_decrement(self):
        a = BigInt(5)
        assert a.pre_decrement() is a
        assert a == BigInt(4)


class TestConversion:
    def test_int_conversion(self):
        assert int(BigInt("-12345")) == -12345

    def test_float_conversion(self):
        assert float(BigInt("123")) == 123.0

    def test_str_and_repr(self):
        assert str(BigInt("-7")) == "-7"
        assert repr(BigInt("-7")) == "BigInt('-7')"

    def test_from_string_and_to_string(self):
        a = BigInt.from_string("-998877665544332211")
        assert a.to_string() == "-998877665544332211"

    def test_copy(self):
        a = BigInt("12345678901234567890")
        b = a.copy()
        assert a == b and a is not b
