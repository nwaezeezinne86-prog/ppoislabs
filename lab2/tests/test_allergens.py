"""Tests for Allergen and AllergenSet."""
import pytest

from lab2.src.allergens import Allergen, AllergenSet
from lab2.src.exceptions import AllergenConflictError


class TestAllergenSet:
    def test_empty(self):
        s = AllergenSet()
        assert s.is_empty()

    def test_add(self):
        s = AllergenSet()
        s.add(Allergen.GLUTEN)
        assert s.contains(Allergen.GLUTEN)
        assert not s.is_empty()

    def test_remove(self):
        s = AllergenSet([Allergen.GLUTEN, Allergen.NUTS])
        s.remove(Allergen.GLUTEN)
        assert not s.contains(Allergen.GLUTEN)
        assert s.contains(Allergen.NUTS)

    def test_remove_missing_ok(self):
        s = AllergenSet([Allergen.GLUTEN])
        s.remove(Allergen.NUTS)   # no error

    def test_union(self):
        a = AllergenSet([Allergen.GLUTEN])
        b = AllergenSet([Allergen.NUTS])
        u = a.union(b)
        assert u.contains(Allergen.GLUTEN)
        assert u.contains(Allergen.NUTS)
        # a and b unchanged
        assert not a.contains(Allergen.NUTS)

    def test_intersects(self):
        a = AllergenSet([Allergen.GLUTEN, Allergen.NUTS])
        b = AllergenSet([Allergen.NUTS])
        assert a.intersects(b)

    def test_no_intersection(self):
        a = AllergenSet([Allergen.GLUTEN])
        b = AllergenSet([Allergen.NUTS])
        assert not a.intersects(b)

    def test_check_compatibility_pass(self):
        s = AllergenSet([Allergen.NUTS])
        forbidden = AllergenSet([Allergen.GLUTEN])
        s.check_compatibility(forbidden)   # no error

    def test_check_compatibility_fail(self):
        s = AllergenSet([Allergen.NUTS])
        forbidden = AllergenSet([Allergen.NUTS])
        with pytest.raises(AllergenConflictError):
            s.check_compatibility(forbidden)

    def test_eq(self):
        assert AllergenSet([Allergen.GLUTEN]) == AllergenSet([Allergen.GLUTEN])
        assert AllergenSet([Allergen.GLUTEN]) != AllergenSet([Allergen.NUTS])

    def test_eq_other_type(self):
        assert AllergenSet([Allergen.GLUTEN]).__eq__(1) is NotImplemented

    def test_hash(self):
        assert hash(AllergenSet([Allergen.GLUTEN])) == hash(AllergenSet([Allergen.GLUTEN]))

    def test_str_empty(self):
        assert AllergenSet().to_str() if False else True  # placeholder
        assert str(AllergenSet()) == "(no allergens)"

    def test_str_nonempty_sorted(self):
        s = AllergenSet([Allergen.NUTS, Allergen.GLUTEN])
        assert str(s) == "gluten, nuts"

    def test_repr(self):
        s = AllergenSet([Allergen.GLUTEN])
        assert "AllergenSet" in repr(s)

    def test_as_set_returns_copy(self):
        s = AllergenSet([Allergen.GLUTEN])
        copy = s.as_set()
        copy.add(Allergen.NUTS)
        assert not s.contains(Allergen.NUTS)
