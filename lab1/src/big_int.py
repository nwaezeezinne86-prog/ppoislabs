"""Signed arbitrary-precision integer module."""
from __future__ import annotations
from typing import Union

__all__ = ["BigInt"]
_DECIMAL_DIGITS = "0123456789"


class BigInt:
    """Signed integer of unbounded length."""

    def __init__(self, value: Union[int, str, "BigInt"] = 0) -> None:
        if isinstance(value, BigInt):
            self._sign: int = value._sign
            self._digits: list[int] = value._digits.copy()
            return
        if isinstance(value, int):
            self._from_int(value)
            return
        if isinstance(value, str):
            self._from_str(value)
            return
        raise TypeError(f"Unsupported type for BigInt: {type(value)!r}")

    def _from_int(self, value: int) -> None:
        if value == 0:
            self._sign = 0
            self._digits = [0]
            return
        self._sign = 1 if value > 0 else -1
        digits: list[int] = []
        n = abs(value)
        while n > 0:
            digits.append(n % 10)
            n //= 10
        self._digits = digits or [0]

    def _from_str(self, value: str) -> None:
        s = value.strip()
        if not s:
            raise ValueError("Empty string is not a valid BigInt")
        sign = 1
        if s[0] in "+-":
            sign = -1 if s[0] == "-" else 1
            s = s[1:]
        if not s or any(ch not in _DECIMAL_DIGITS for ch in s):
            raise ValueError(f"Invalid BigInt literal: {value!r}")
        digits = [int(ch) for ch in reversed(s)]
        self._digits = self._strip_zeros(digits)
        self._sign = 0 if self._digits == [0] else sign

    @staticmethod
    def _strip_zeros(digits: list[int]) -> list[int]:
        while len(digits) > 1 and digits[-1] == 0:
            digits.pop()
        return digits

    @property
    def sign(self) -> int:
        """Sign: -1, 0, or 1."""
        return self._sign

    @property
    def is_zero(self) -> bool:
        """True if zero."""
        return self._sign == 0

    @staticmethod
    def _cmp_abs(a, b):
        if len(a) != len(b):
            return 1 if len(a) > len(b) else -1
        for x, y in zip(reversed(a), reversed(b)):
            if x != y:
                return 1 if x > y else -1
        return 0

    def __eq__(self, other):
        if isinstance(other, int):
            other = BigInt(other)
        if not isinstance(other, BigInt):
            return NotImplemented
        return self._sign == other._sign and self._digits == other._digits

    def __hash__(self):
        return hash((self._sign, tuple(self._digits)))

    def __lt__(self, other):
        other = BigInt(other) if isinstance(other, int) else other
        if self._sign != other._sign:
            return self._sign < other._sign
        if self._sign == 0:
            return False
        c = self._cmp_abs(self._digits, other._digits)
        return c < 0 if self._sign > 0 else c > 0

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    @staticmethod
    def _add_abs(a, b):
        result, carry = [], 0
        for i in range(max(len(a), len(b))):
            da = a[i] if i < len(a) else 0
            db = b[i] if i < len(b) else 0
            s = da + db + carry
            result.append(s % 10)
            carry = s // 10
        if carry:
            result.append(carry)
        return result

    @staticmethod
    def _sub_abs(a, b):
        result, borrow = [], 0
        for i in range(len(a)):
            da = a[i]
            db = b[i] if i < len(b) else 0
            diff = da - db - borrow
            if diff < 0:
                diff += 10
                borrow = 1
            else:
                borrow = 0
            result.append(diff)
        return BigInt._strip_zeros(result)

    def __add__(self, other):
        other = BigInt(other) if isinstance(other, int) else other
        if not isinstance(other, BigInt):
            return NotImplemented
        if self._sign == 0:
            return BigInt(other)
        if other._sign == 0:
            return BigInt(self)
        if self._sign == other._sign:
            r = BigInt(0)
            r._digits = self._add_abs(self._digits, other._digits)
            r._sign = self._sign
            return r
        c = self._cmp_abs(self._digits, other._digits)
        if c == 0:
            return BigInt(0)
        r = BigInt(0)
        if c > 0:
            r._digits = self._sub_abs(self._digits, other._digits)
            r._sign = self._sign
        else:
            r._digits = self._sub_abs(other._digits, self._digits)
            r._sign = other._sign
        return r

    def __neg__(self):
        r = BigInt(self)
        r._sign = -r._sign
        return r

    def __sub__(self, other):
        other = BigInt(other) if isinstance(other, int) else other
        if not isinstance(other, BigInt):
            return NotImplemented
        return self + (-other)

    def __mul__(self, other):
        other = BigInt(other) if isinstance(other, int) else other
        if not isinstance(other, BigInt):
            return NotImplemented
        if self._sign == 0 or other._sign == 0:
            return BigInt(0)
        result = [0] * (len(self._digits) + len(other._digits))
        for i, da in enumerate(self._digits):
            carry = 0
            for j, db in enumerate(other._digits):
                cur = result[i + j] + da * db + carry
                result[i + j] = cur % 10
                carry = cur // 10
            k = i + len(other._digits)
            while carry:
                cur = result[k] + carry
                result[k] = cur % 10
                carry = cur // 10
                k += 1
        out = BigInt(0)
        out._digits = BigInt._strip_zeros(result)
        out._sign = self._sign * other._sign
        return out

    @staticmethod
    def _divmod_abs(a, b):
        if BigInt._cmp_abs(a, b) < 0:
            return [0], a[:]
        q = [0] * len(a)
        rem = []
        for i in range(len(a) - 1, -1, -1):
            rem.insert(0, a[i])
            rem = BigInt._strip_zeros(rem)
            d = 0
            while BigInt._cmp_abs(rem, b) >= 0:
                rem = BigInt._sub_abs(rem, b)
                d += 1
            q[i] = d
        return BigInt._strip_zeros(q), rem

    def __floordiv__(self, other):
        other = BigInt(other) if isinstance(other, int) else other
        if not isinstance(other, BigInt):
            return NotImplemented
        if other._sign == 0:
            raise ZeroDivisionError("BigInt division by zero")
        q, _ = self._divmod_abs(self._digits, other._digits)
        r = BigInt(0)
        r._digits = q
        r._sign = 0 if q == [0] else self._sign * other._sign
        return r

    def __truediv__(self, other):
        return self.__floordiv__(other)

    def __mod__(self, other):
        other = BigInt(other) if isinstance(other, int) else other
        if not isinstance(other, BigInt):
            return NotImplemented
        if other._sign == 0:
            raise ZeroDivisionError("BigInt modulo by zero")
        _, rem = self._divmod_abs(self._digits, other._digits)
        r = BigInt(0)
        r._digits = rem
        r._sign = 0 if rem == [0] else self._sign
        return r

    def __iadd__(self, other):
        r = self + other
        self._sign, self._digits = r._sign, r._digits
        return self

    def __isub__(self, other):
        r = self - other
        self._sign, self._digits = r._sign, r._digits
        return self

    def __imul__(self, other):
        r = self * other
        self._sign, self._digits = r._sign, r._digits
        return self

    def __ifloordiv__(self, other):
        r = self // other
        self._sign, self._digits = r._sign, r._digits
        return self

    def increment(self):
        """Post-increment."""
        old = BigInt(self)
        self += BigInt(1)
        return old

    def decrement(self):
        """Post-decrement."""
        old = BigInt(self)
        self -= BigInt(1)
        return old

    def pre_increment(self):
        """Pre-increment."""
        self += BigInt(1)
        return self

    def pre_decrement(self):
        """Pre-decrement."""
        self -= BigInt(1)
        return self

    def __int__(self):
        v = 0
        for d in reversed(self._digits):
            v = v * 10 + d
        return v * self._sign

    def __float__(self):
        return float(int(self))

    def __str__(self):
        if self._sign == 0:
            return "0"
        body = "".join(str(d) for d in reversed(self._digits))
        return f"-{body}" if self._sign < 0 else body

    def __repr__(self):
        return f"BigInt('{self}')"

    @classmethod
    def from_string(cls, text):
        """Create a BigInt from a string."""
        return cls(text)

    def to_string(self):
        """Return the string representation."""
        return str(self)

    def copy(self):
        """Return an independent copy."""
        return BigInt(self)
