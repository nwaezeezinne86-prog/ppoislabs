"""Tests for recipes and recipe book."""
from datetime import date

import pytest

from lab2.src.allergens import Allergen, AllergenSet
from lab2.src.exceptions import IngredientNotFoundError, RecipeNotFoundError
from lab2.src.ingredients import Ingredient, Vegetable
from lab2.src.money import Money
from lab2.src.nutrition import Nutrition
from lab2.src.recipes import (
    Recipe,
    RecipeAnalyzer,
    RecipeBook,
    RecipeIngredient,
    RecipeStep,
)
from lab2.src.technique import Boil
from lab2.src.units import Quantity, Unit


def _tomato():
    return Vegetable("Tomato", Unit.KILOGRAM, Money.from_major(150.0), 5, 9)


def _simple_recipe(name: str = "Soup", servings: int = 4) -> Recipe:
    r = Recipe(name, servings)
    r.add_ingredient(RecipeIngredient(_tomato(), Quantity(0.5, Unit.KILOGRAM)))
    r.add_step(RecipeStep(1, "Boil", Boil(), 15))
    return r


class TestRecipeStep:
    def test_bad_number(self):
        with pytest.raises(ValueError):
            RecipeStep(0, "x", Boil(), 10)

    def test_bad_minutes(self):
        with pytest.raises(ValueError):
            RecipeStep(1, "x", Boil(), 0)

    def test_perform(self):
        step = RecipeStep(1, "Boil", Boil(), 5)
        assert "Boiled" in step.perform("potato")

    def test_describe(self):
        step = RecipeStep(1, "Boil", Boil(), 5)
        assert "Boil" in step.describe()

    def test_repr_and_str(self):
        step = RecipeStep(1, "Boil", Boil(), 5)
        assert "Boil" in str(step)
        assert "RecipeStep" in repr(step)


class TestRecipeIngredient:
    def test_cost(self):
        item = RecipeIngredient(_tomato(), Quantity(0.5, Unit.KILOGRAM))
        assert item.cost() == Money.from_major(75.0)

    def test_scale(self):
        item = RecipeIngredient(_tomato(), Quantity(0.5, Unit.KILOGRAM))
        scaled = item.scale(2.0)
        assert scaled.quantity.amount == 1.0

    def test_describe_with_note(self):
        item = RecipeIngredient(_tomato(), Quantity(0.5, Unit.KILOGRAM), "diced")
        assert "diced" in item.describe()

    def test_repr(self):
        item = RecipeIngredient(_tomato(), Quantity(0.5, Unit.KILOGRAM))
        assert "RecipeIngredient" in repr(item)


class TestRecipe:
    def test_empty_name(self):
        with pytest.raises(ValueError):
            Recipe("", 2)

    def test_bad_servings(self):
        with pytest.raises(ValueError):
            Recipe("X", 0)

    def test_remove_ingredient(self):
        r = _simple_recipe()
        r.remove_ingredient("Tomato")
        assert r.ingredient_count() == 0

    def test_remove_missing_ingredient(self):
        r = _simple_recipe()
        with pytest.raises(IngredientNotFoundError):
            r.remove_ingredient("Banana")

    def test_add_step_out_of_order(self):
        r = Recipe("X")
        with pytest.raises(ValueError):
            r.add_step(RecipeStep(2, "x", Boil(), 5))

    def test_time_cost(self):
        r = _simple_recipe()
        assert r.total_time_minutes() == 15
        assert r.total_cost() == Money.from_major(75.0)
        assert r.cost_per_serving() == Money.from_major(18.75)

    def test_empty_recipe_cost_zero(self):
        r = Recipe("Empty")
        assert r.total_cost().is_zero()
        assert r.cost_per_serving().is_zero()

    def test_allergens_union(self):
        r = _simple_recipe()
        # tomato has no allergens set
        assert r.allergens().is_empty()

    def test_scale_recipe(self):
        r = _simple_recipe()
        scaled = r.scale(2.0)
        assert scaled.ingredient_count() == 1
        assert scaled.step_count() == 1
        assert "x2" in scaled.name

    def test_nutrition_per_serving(self):
        r = _simple_recipe()
        r.set_nutrition(Nutrition(10, 5, 20))
        result = r.nutrition_per_serving()
        assert result.protein_g == 40

    def test_describe(self):
        r = _simple_recipe()
        text = r.describe()
        assert "Soup" in text
        assert "Tomato" in text

    def test_str(self):
        r = _simple_recipe()
        assert "Soup" in str(r)

    def test_repr(self):
        r = _simple_recipe()
        assert "Recipe(" in repr(r)


class TestRecipeBook:
    def test_add_and_find(self):
        book = RecipeBook()
        book.add(_simple_recipe("Soup"))
        assert book.find("soup").name == "Soup"

    def test_find_missing(self):
        with pytest.raises(RecipeNotFoundError):
            RecipeBook().find("Pizza")

    def test_remove(self):
        book = RecipeBook()
        book.add(_simple_recipe("Soup"))
        book.remove("Soup")
        assert book.count() == 0

    def test_remove_missing(self):
        with pytest.raises(RecipeNotFoundError):
            RecipeBook().remove("Pizza")

    def test_add_replaces(self):
        book = RecipeBook()
        book.add(_simple_recipe("Soup"))
        book.add(_simple_recipe("Soup"))
        assert book.count() == 1

    def test_all_filters(self):
        book = RecipeBook()
        book.add(_simple_recipe("Soup"))
        assert len(book.find_cheaper_than(Money.from_major(100))) == 1
        assert len(book.find_cheaper_than(Money.from_major(10))) == 0
        assert len(book.find_faster_than(20)) == 1
        assert len(book.find_faster_than(5)) == 0

    def test_total_cost_empty(self):
        assert RecipeBook().total_cost().is_zero()

    def test_total_cost_nonempty(self):
        book = RecipeBook()
        book.add(_simple_recipe("Soup"))
        assert book.total_cost() == Money.from_major(75.0)

    def test_len_str_repr(self):
        book = RecipeBook("My")
        book.add(_simple_recipe("Soup"))
        assert len(book) == 1
        assert "My" in str(book)
        assert "RecipeBook" in repr(book)


class TestRecipeAnalyzer:
    def test_ingredient_names(self):
        analyzer = RecipeAnalyzer(_simple_recipe())
        assert analyzer.ingredient_names() == ["Tomato"]

    def test_most_expensive(self):
        analyzer = RecipeAnalyzer(_simple_recipe())
        assert analyzer.most_expensive_ingredient() == "Tomato"

    def test_most_expensive_empty(self):
        with pytest.raises(IngredientNotFoundError):
            RecipeAnalyzer(Recipe("X")).most_expensive_ingredient()

    def test_avg_step_minutes_empty(self):
        assert RecipeAnalyzer(Recipe("X")).average_step_minutes() == 0.0

    def test_avg_step_minutes(self):
        analyzer = RecipeAnalyzer(_simple_recipe())
        assert analyzer.average_step_minutes() == 15.0

    def test_cost_breakdown(self):
        analyzer = RecipeAnalyzer(_simple_recipe())
        assert "Tomato" in analyzer.cost_breakdown()

    def test_low_calorie(self):
        r = _simple_recipe()
        r.set_nutrition(Nutrition(0, 0, 0))
        assert RecipeAnalyzer(r).is_low_calorie()

    def test_technique_count(self):
        analyzer = RecipeAnalyzer(_simple_recipe())
        assert analyzer.technique_count() == 1

    def test_summary(self):
        assert "Soup" in RecipeAnalyzer(_simple_recipe()).summary()
