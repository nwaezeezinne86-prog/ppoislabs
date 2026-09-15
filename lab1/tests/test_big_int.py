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


class TestEdgeCases:
    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            BigInt("")

    def test_whitespace_only_string_raises_value_error(self):
        with pytest.raises(ValueError):
            BigInt("   ")

    def test_zero_str_after_sign(self):
        assert str(BigInt("-0")) == "0"
        assert str(BigInt("+0")) == "0"

    def test_eq_unsupported_type_returns_not_implemented(self):
        assert BigInt(1).__eq__(None) is NotImplemented

    def test_truediv_uses_floordiv(self):
        assert BigInt(9) / BigInt(2) == BigInt(4)

    def test_truediv_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            BigInt(1) / BigInt(0)

    def test_floordiv_negative_divisor(self):
        assert BigInt(10) // BigInt(-3) == BigInt(-3)

    def test_mod_negative_divisor(self):
        assert BigInt(10) % BigInt(-3) == BigInt(1)

    def test_add_other_type_returns_not_implemented(self):
        assert BigInt(1).__add__("x") is NotImplemented

    def test_sub_other_type_returns_not_implemented(self):
        assert BigInt(1).__sub__("x") is NotImplemented

    def test_mul_other_type_returns_not_implemented(self):
        assert BigInt(1).__mul__("x") is NotImplemented

    def test_floordiv_other_type_returns_not_implemented(self):
        assert BigInt(1).__floordiv__("x") is NotImplemented

    def test_mod_other_type_returns_not_implemented(self):
        assert BigInt(1).__mod__("x") is NotImplemented

    def test_str_of_zero(self):
        assert str(BigInt(0)) == "0"

    def test_lt_same_length_different_digits(self):
        assert BigInt(19) < BigInt(21)
        assert BigInt(-19) > BigInt(-21)

    def test_lt_with_int(self):
        assert BigInt(3) < 5

    def test_le_with_int(self):
        assert BigInt(5) <= 5

    def test_gt_with_int(self):
        assert BigInt(5) > 3

    def test_ge_with_int(self):
        assert BigInt(5) >= 5

    def test_div_mod_signs(self):
        assert BigInt(-10) // BigInt(3) == BigInt(-4)
        assert BigInt(-10) % BigInt(3) == BigInt(-1)
        assert BigInt(10) // BigInt(-3) == BigInt(-4)
        assert BigInt(10) % BigInt(-3) == BigInt(1)

    def test_mul_negative_by_negative(self):
        assert BigInt(-4) * BigInt(-5) == BigInt(20)

    def test_sub_same_value_returns_zero(self):
        assert BigInt(7) - BigInt(7) == BigInt(0)


class TestEdgeCases:
    def test_str_with_plus_sign_keeps_positive(self):
        assert BigInt("+0") == BigInt(0)

    def test_str_with_leading_zeros(self):
        assert str(BigInt("0000")) == "0"
        assert str(BigInt("-0000")) == "0"

    def test_str_sign_then_non_digit(self):
        with pytest.raises(ValueError):
            BigInt("+abc")

    def test_iadd_with_int(self):
        a = BigInt(5)
        a += 7
        assert a == BigInt(12)

    def test_isub_with_int(self):
        a = BigInt(5)
        a -= 7
        assert a == BigInt(-2)

    def test_imul_with_int(self):
        a = BigInt(5)
        a *= 3
        assert a == BigInt(15)

    def test_ifloordiv_with_int(self):
        a = BigInt(20)
        a //= 6
        assert a == BigInt(3)

    def test_truediv_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            BigInt(1) / BigInt(0)

    def test_mod_by_negative(self):
        assert BigInt(7) % BigInt(-3) == BigInt(1)

    def test_sub_returns_notimplemented_for_str(self):
        assert BigInt(1).__sub__("x") is NotImplemented

    def test_mul_returns_notimplemented_for_str(self):
        assert BigInt(1).__mul__("x") is NotImplemented

    def test_add_returns_notimplemented_for_str(self):
        assert BigInt(1).__add__("x") is NotImplemented

    def test_floordiv_returns_notimplemented_for_str(self):
        assert BigInt(1).__floordiv__("x") is NotImplemented

    def test_mod_returns_notimplemented_for_str(self):
        assert BigInt(1).__mod__("x") is NotImplemented

    def test_str_with_trailing_zeros(self):
        # covers _strip_zeros path with multiple digits
        assert str(BigInt("1000")) == "1000"
        assert str(BigInt("1000") - BigInt("1000")) == "0"

    def test_sub_equal_abs(self):
        assert BigInt(5) - BigInt(5) == BigInt(0)
        assert BigInt(-5) - BigInt(-5) == BigInt(0)

    def test_copy_independent_negative(self):
        a = BigInt(-42)
        b = a.copy()
        b.pre_increment()
        assert a == BigInt(-42)
        assert b == BigInt(-41)


class TestLastMissingLines:
    def test_mul_by_str_returns_notimplemented(self):
        assert BigInt(3).__mul__("oops") is NotImplemented

    def test_neg_of_zero(self):
        assert -BigInt(0) == BigInt(0)

    def test_add_return_notimplemented_directly(self):
        assert BigInt(3).__add__([1, 2]) is NotImplemented
