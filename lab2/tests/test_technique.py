"""Tests for cooking techniques."""
import pytest

from lab2.src.exceptions import OvercookedError
from lab2.src.technique import Bake, Boil, Fry, Grill, Mix, SousVide, Steam


class TestBoil:
    def test_apply(self):
        assert "Boiled" in Boil().apply("egg", 5)

    def test_overcooked(self):
        with pytest.raises(OvercookedError):
            Boil(default_minutes=5).apply("egg", 100)

    def test_scale_water(self):
        assert Boil(water_ml=500).scale_water(2.0) == 1000


class TestFry:
    def test_apply(self):
        assert "Fried" in Fry().apply("egg", 3)

    def test_overcooked(self):
        with pytest.raises(OvercookedError):
            Fry(default_minutes=3).apply("egg", 100)

    def test_deep_fry(self):
        assert Fry(oil_ml=300).is_deep_fry()
        assert not Fry(oil_ml=30).is_deep_fry()


class TestBake:
    def test_apply(self):
        assert "Baked" in Bake().apply("cake", 30)

    def test_overcooked(self):
        with pytest.raises(OvercookedError):
            Bake(default_minutes=10).apply("cake", 100)

    def test_lower_temperature_floor(self):
        b = Bake(temperature_c=70)
        b.lower_temperature(100)
        assert b.apply("x", 1).find("60") >= 0


class TestGrill:
    def test_apply(self):
        assert "Grilled" in Grill().apply("steak", 5)

    def test_overcooked(self):
        with pytest.raises(OvercookedError):
            Grill(default_minutes=3).apply("steak", 100)

    def test_high_heat(self):
        assert Grill(flame_level=9).is_high_heat()
        assert not Grill(flame_level=2).is_high_heat()


class TestSteam:
    def test_apply(self):
        assert "Steamed" in Steam().apply("fish", 10)

    def test_overcooked(self):
        with pytest.raises(OvercookedError):
            Steam(default_minutes=3).apply("fish", 100)

    def test_pressure_cooking(self):
        assert Steam(pressure_bar=2.0).is_pressure_cooking()
        assert not Steam(pressure_bar=1.0).is_pressure_cooking()


class TestSousVide:
    def test_apply(self):
        assert "Sous-vide" in SousVide().apply("beef", 90)

    def test_too_short(self):
        with pytest.raises(OvercookedError):
            SousVide(default_minutes=60).apply("beef", 10)

    def test_low_temp(self):
        assert SousVide(temperature_c=55).is_low_temp()
        assert not SousVide(temperature_c=80).is_low_temp()


class TestMix:
    def test_apply(self):
        assert "Mixed" in Mix().apply("cream", 3)

    def test_high_speed(self):
        assert Mix(speed=5).is_high_speed()
        assert not Mix(speed=1).is_high_speed()


class TestCommon:
    def test_technique_name_and_default(self):
        b = Boil()
        assert b.name == "boil"
        assert b.default_minutes == 15

    def test_describe(self):
        assert "boil" in Boil().describe().lower()

    def test_str(self):
        assert str(Boil()) == "boil"
