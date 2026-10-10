import unittest
from datetime import datetime, timedelta

from fitness.exceptions import InvalidNutritionDataException
from fitness.nutrition import Food, Meal, MealPlan, NutritionLog, Recipe
from tests.factories import NOW, TODAY, make_user

OATS = Food("Oats", 150.0, 5.0, 27.0, 3.0)
EGG = Food("Egg", 80.0, 6.0, 1.0, 5.0)


class FoodTest(unittest.TestCase):
    def test_macros(self):
        OATS.validate()
        self.assertEqual(OATS.macro_calories(), 5 * 4 + 27 * 4 + 3 * 9)

    def test_scaled(self):
        double = OATS.scaled(2)
        self.assertEqual(double.calories, 300.0)
        with self.assertRaises(InvalidNutritionDataException):
            OATS.scaled(0)

    def test_invalid(self):
        with self.assertRaises(InvalidNutritionDataException):
            Food("Bad", -1.0, 0.0, 0.0, 0.0).validate()


class MealTest(unittest.TestCase):
    def test_totals(self):
        meal = Meal("breakfast", NOW)
        meal.validate()
        meal.add_food(OATS)
        meal.add_food(EGG)
        self.assertEqual(meal.total_calories(), 230.0)
        self.assertEqual(meal.total_protein(), 11.0)
        self.assertAlmostEqual(sum(meal.macro_split().values()), 100.0)

    def test_empty_split_and_invalid(self):
        self.assertEqual(Meal("lunch", NOW).macro_split()["fat"], 0.0)
        with self.assertRaises(InvalidNutritionDataException):
            Meal("brunch", NOW).validate()
        with self.assertRaises(InvalidNutritionDataException):
            Meal("lunch", NOW).add_food(Food("Bad", -1.0, 0.0, 0.0, 0.0))


class RecipeTest(unittest.TestCase):
    def test_recipe(self):
        recipe = Recipe("Omelette", 2)
        recipe.add_ingredient(EGG)
        recipe.add_ingredient(EGG)
        self.assertEqual(recipe.total_calories(), 160.0)
        self.assertEqual(recipe.calories_per_serving(), 80.0)
        meal = recipe.to_meal("dinner", NOW)
        self.assertEqual(meal.total_calories(), 80.0)

    def test_invalid_servings(self):
        with self.assertRaises(InvalidNutritionDataException):
            Recipe("Empty", 0).calories_per_serving()
        with self.assertRaises(InvalidNutritionDataException):
            Recipe("Bad", 1).add_ingredient(Food("Bad", -1.0, 0.0, 0.0, 0.0))


class MealPlanTest(unittest.TestCase):
    def test_plan(self):
        plan = MealPlan(make_user(), 200.0)
        meal = Meal("lunch", NOW, [EGG])
        plan.add_meal(meal)
        self.assertEqual(plan.planned_calories(), 80.0)
        self.assertEqual(plan.remaining_calories(), 120.0)
        self.assertTrue(plan.is_within_target())
        plan.add_meal(Meal("dinner", NOW, [OATS]))
        self.assertFalse(plan.is_within_target())

    def test_invalid_meal(self):
        with self.assertRaises(InvalidNutritionDataException):
            MealPlan(make_user(), 100.0).add_meal(Meal("brunch", NOW))


class NutritionLogTest(unittest.TestCase):
    def test_log(self):
        log = NutritionLog(make_user())
        self.assertEqual(log.average_daily_calories(), 0.0)
        log.log_meal(Meal("breakfast", NOW, [OATS]))
        log.log_meal(Meal("lunch", NOW, [EGG]))
        log.log_meal(Meal("lunch", NOW - timedelta(days=1), [EGG]))
        self.assertEqual(log.calories_on(TODAY), 230.0)
        self.assertEqual(log.protein_on(TODAY), 11.0)
        self.assertEqual(log.average_daily_calories(), 155.0)

    def test_invalid_meal(self):
        with self.assertRaises(InvalidNutritionDataException):
            NutritionLog(make_user()).log_meal(Meal("brunch", datetime.now()))
