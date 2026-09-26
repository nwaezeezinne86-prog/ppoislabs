"""Tests for Nutrition and NutritionTracker."""
import pytest

from lab2.src.exceptions import InvalidQuantityError
from lab2.src.nutrition import Nutrition, NutritionTracker


class TestNutrition:
    def test_negative_value(self):
        with pytest.raises(InvalidQuantityError):
            Nutrition(-1.0, 0.0, 0.0)

    def test_kcal(self):
        n = Nutrition(10.0, 5.0, 20.0)
        expected = 10 * 4 + 5 * 9 + 20 * 4
        assert n.kcal() == expected

    def test_is_low_carb(self):
        assert Nutrition(0, 0, 5).is_low_carb()
        assert not Nutrition(0, 0, 20).is_low_carb()

    def test_is_high_protein(self):
        assert Nutrition(25, 0, 0).is_high_protein()
        assert not Nutrition(5, 0, 0).is_high_protein()

    def test_scale(self):
        n = Nutrition(10, 5, 20)
        s = n.scale(2)
        assert (s.protein_g, s.fat_g, s.carbs_g) == (20, 10, 40)

    def test_add(self):
        a = Nutrition(10, 5, 20)
        b = Nutrition(1, 2, 3)
        c = a + b
        assert (c.protein_g, c.fat_g, c.carbs_g) == (11, 7, 23)


class TestNutritionTracker:
    def test_empty_total(self):
        t = NutritionTracker()
        assert t.total().kcal() == 0.0

    def test_add_and_total(self):
        t = NutritionTracker()
        t.add(Nutrition(10, 5, 20))
        t.add(Nutrition(10, 5, 20))
        assert t.entry_count() == 2
        assert t.total().protein_g == 20

    def test_remaining_kcal(self):
        t = NutritionTracker(daily_kcal_limit=2000)
        t.add(Nutrition(0, 0, 100))   # 400 kcal
        assert t.remaining_kcal() == pytest.approx(1600.0)

    def test_over_limit(self):
        t = NutritionTracker(daily_kcal_limit=100)
        t.add(Nutrition(100, 0, 0))   # 400 kcal > 100
        assert t.is_over_limit()

    def test_reset(self):
        t = NutritionTracker()
        t.add(Nutrition(10, 0, 0))
        t.reset()
        assert t.entry_count() == 0

    def test_protein_share_empty(self):
        t = NutritionTracker()
        assert t.protein_share() == 0.0

    def test_protein_share_nonzero(self):
        t = NutritionTracker()
        t.add(Nutrition(10, 0, 0))   # only protein: 40 kcal; 100 % protein
        assert t.protein_share() == pytest.approx(1.0)
