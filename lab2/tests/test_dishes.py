"""Tests for dishes, portions, courses and menus."""
import pytest

from lab2.src.dishes import Course, Dish, Menu, MenuPlanner, Portion
from lab2.src.exceptions import InvalidMenuItemError
from lab2.src.ingredients import Vegetable
from lab2.src.money import Money
from lab2.src.nutrition import Nutrition
from lab2.src.recipes import Recipe, RecipeIngredient, RecipeStep
from lab2.src.technique import Boil
from lab2.src.units import Quantity, Unit


def _recipe(name: str = "Soup", servings: int = 4) -> Recipe:
    r = Recipe(name, servings)
    tomato = Vegetable("Tomato", Unit.KILOGRAM, Money.from_major(150.0), 5, 9)
    r.add_ingredient(RecipeIngredient(tomato, Quantity(0.5, Unit.KILOGRAM)))
    r.add_step(RecipeStep(1, "Boil", Boil(), 15))
    r.set_nutrition(Nutrition(5, 3, 12))
    return r


class TestPortion:
    def test_bad_size(self):
        with pytest.raises(ValueError):
            Portion(_recipe(), 0)

    def test_cost(self):
        p = Portion(_recipe(), 1.0)
        assert p.cost() == Money.from_major(18.75)

    def test_nutrition(self):
        p = Portion(_recipe(), 2.0)
        # recipe: servings=4, per-100g protein=5, size_factor=2
        # per serving: 5*4 = 20, times size_factor=2 -> 40
        assert p.nutrition().protein_g == 40

    def test_allergens(self):
        assert Portion(_recipe()).allergens().is_empty()

    def test_describe(self):
        assert "Soup" in Portion(_recipe()).describe()

    def test_str(self):
        assert "Soup" in str(Portion(_recipe()))


class TestDish:
    def test_empty_name(self):
        with pytest.raises(ValueError):
            Dish("", Portion(_recipe()))

    def test_price_for_sale(self):
        d = Dish("Plate", Portion(_recipe()))
        assert d.price_for_sale(2.0) == Money.from_major(37.50)

    def test_garnish_add_remove(self):
        d = Dish("Plate", Portion(_recipe()))
        d.add_garnish("basil")
        d.add_garnish("parsley")
        d.remove_garnish("basil")
        assert "basil" not in d.describe()
        assert "parsley" in d.describe()

    def test_remove_unknown_garnish_ok(self):
        Dish("Plate", Portion(_recipe())).remove_garnish("x")

    def test_describe_with_plating(self):
        d = Dish("Plate", Portion(_recipe()), plating="bowl")
        assert "bowl" in d.describe()

    def test_str(self):
        assert str(Dish("Plate", Portion(_recipe()))) == "Plate"


class TestCourse:
    def test_bad_kind(self):
        with pytest.raises(ValueError):
            Course("unknown")

    def test_add_remove(self):
        c = Course("main")
        d = Dish("Steak", Portion(_recipe()))
        c.add_dish(d)
        assert c.dish_count() == 1
        c.remove_dish("Steak")
        assert c.dish_count() == 0

    def test_remove_missing(self):
        with pytest.raises(InvalidMenuItemError):
            Course("main").remove_dish("x")

    def test_total_cost_empty(self):
        assert Course("main").total_cost().is_zero()

    def test_total_cost(self):
        c = Course("main")
        c.add_dish(Dish("A", Portion(_recipe())))
        c.add_dish(Dish("B", Portion(_recipe())))
        assert c.total_cost() == Money.from_major(37.50)

    def test_list_dishes(self):
        c = Course("main")
        c.add_dish(Dish("Steak", Portion(_recipe())))
        assert c.list_dishes() == ["Steak"]

    def test_str(self):
        c = Course("main")
        c.add_dish(Dish("Steak", Portion(_recipe())))
        assert "Steak" in str(c)


class TestMenu:
    def test_empty_title(self):
        with pytest.raises(ValueError):
            Menu("  ")

    def test_add_course(self):
        menu = Menu("Lunch")
        menu.add_course(Course("main"))
        assert menu.course_count() == 1

    def test_remove_course_missing(self):
        with pytest.raises(InvalidMenuItemError):
            Menu("Lunch").remove_course("main")

    def test_remove_course(self):
        menu = Menu("Lunch")
        menu.add_course(Course("main"))
        menu.remove_course("main")
        assert menu.course_count() == 0

    def test_counts(self):
        menu = Menu("Lunch")
        c = Course("main")
        c.add_dish(Dish("A", Portion(_recipe())))
        menu.add_course(c)
        assert menu.dish_count() == 1

    def test_total_cost_empty(self):
        assert Menu("Lunch").total_cost().is_zero()

    def test_allergens_empty(self):
        menu = Menu("Lunch")
        assert menu.allergens().is_empty()

    def test_check_safe_for(self):
        menu = Menu("Lunch")
        menu.check_safe_for(menu.allergens())  # no error

    def test_describe(self):
        menu = Menu("Lunch")
        c = Course("main")
        c.add_dish(Dish("Steak", Portion(_recipe())))
        menu.add_course(c)
        assert "Lunch" in menu.describe()

    def test_str(self):
        assert str(Menu("Lunch")) == "Lunch"


class TestMenuPlanner:
    def test_count(self):
        p = MenuPlanner([_recipe()])
        assert p.count_recipes() == 1

    def test_cheapest(self):
        p = MenuPlanner([_recipe("A"), _recipe("B")])
        assert p.cheapest() is not None

    def test_cheapest_empty(self):
        with pytest.raises(InvalidMenuItemError):
            MenuPlanner([]).cheapest()

    def test_build_menu(self):
        planner = MenuPlanner([_recipe("A"), _recipe("B"), _recipe("C")])
        menu = planner.build_menu("Test", 1, 1, 1)
        assert menu.course_count() == 3
        assert menu.dish_count() >= 1

    def test_pick_for_course_empty(self):
        assert MenuPlanner([]).pick_for_course("starter") == []
