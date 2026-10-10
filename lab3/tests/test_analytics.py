import unittest
from datetime import timedelta

from fitness.activities import CardioActivity
from fitness.analytics import BMICalculator, CalorieCalculator, ProgressAnalyzer, ProgressReport
from fitness.exceptions import GoalNotAchievableException, InvalidMeasurementException, InvalidWorkoutException
from fitness.goals import WeightGoal
from fitness.exercises import Workout
from tests.factories import NOW, TODAY, make_exercise, make_profile, make_set, make_user, make_workout


class BMICalculatorTest(unittest.TestCase):
    def test_calculate_and_category(self):
        calculator = BMICalculator()
        self.assertEqual(calculator.calculate(80.0, 1.8), 24.7)
        self.assertEqual(calculator.category(17.0), "underweight")
        self.assertEqual(calculator.category(22.0), "normal")
        self.assertEqual(calculator.category(27.0), "overweight")
        self.assertEqual(calculator.category(35.0), "obese")
        self.assertEqual(calculator.classify(make_profile()), "normal")

    def test_invalid_height(self):
        with self.assertRaises(InvalidMeasurementException):
            BMICalculator().calculate(80.0, 0.0)


class CalorieCalculatorTest(unittest.TestCase):
    def test_rates(self):
        calculator = CalorieCalculator()
        self.assertEqual(calculator.basal_rate(make_profile("male"), 30), 1780.0)
        self.assertEqual(calculator.basal_rate(make_profile("female"), 30), 1614.0)
        self.assertEqual(calculator.daily_needs(make_profile("male"), 30), 2759.0)
        self.assertEqual(calculator.calories_for_weight_change(1.0), 7700.0)

    def test_daily_adjustment(self):
        goal = WeightGoal(1, "Cut", 76.0, TODAY + timedelta(days=28), make_user(), 80.0, 80.0)
        self.assertEqual(CalorieCalculator().daily_adjustment(goal, TODAY), -1100.0)
        with self.assertRaises(GoalNotAchievableException):
            CalorieCalculator().daily_adjustment(goal, TODAY + timedelta(days=28))


def make_report(workouts: list[Workout], with_run: bool = False) -> ProgressReport:
    user = make_user()
    runs = [CardioActivity(1, user, NOW, 30.0, 5.0)] if with_run else []
    return ProgressReport(user, TODAY - timedelta(days=7), TODAY, workouts, runs)


class ProgressReportTest(unittest.TestCase):
    def test_totals(self):
        report = make_report([make_workout()], with_run=True)
        self.assertEqual(report.total_workouts(), 2)
        self.assertEqual(report.total_volume(), 980.0)
        self.assertEqual(report.total_distance_km(), 5.0)
        self.assertEqual(report.average_workout_minutes(), 45.0)
        self.assertGreater(report.total_calories(), 0)

    def test_empty(self):
        report = make_report([])
        self.assertEqual(report.average_workout_minutes(), 0.0)
        self.assertEqual(report.total_calories(), 0.0)


class ProgressAnalyzerTest(unittest.TestCase):
    def test_compare_volume(self):
        light, heavy = Workout(1, "L", TODAY, 30), Workout(2, "H", TODAY, 30)
        light.add_set(make_set(10, 50.0))
        heavy.add_set(make_set(10, 60.0))
        analyzer = ProgressAnalyzer()
        self.assertEqual(analyzer.compare_volume(make_report([light]), make_report([heavy])), 20.0)
        self.assertEqual(analyzer.compare_volume(make_report([]), make_report([heavy])), 0.0)

    def test_trend(self):
        analyzer = ProgressAnalyzer()
        self.assertEqual(analyzer.trend([100.0, 120.0]), "improving")
        self.assertEqual(analyzer.trend([100.0, 80.0]), "declining")
        self.assertEqual(analyzer.trend([100.0, 101.0]), "stable")
        self.assertEqual(analyzer.trend([5.0]), "stable")
        self.assertEqual(analyzer.trend([0.0, 5.0]), "stable")

    def test_best_workout_and_record(self):
        light, heavy = Workout(1, "L", TODAY, 30), Workout(2, "H", TODAY, 30)
        light.add_set(make_set(10, 50.0))
        heavy.add_set(make_set(10, 80.0))
        analyzer = ProgressAnalyzer()
        self.assertEqual(analyzer.best_workout([light, heavy]), heavy)
        self.assertAlmostEqual(analyzer.personal_record([light, heavy], make_exercise()), 106.67, places=1)
        self.assertEqual(analyzer.personal_record([light], make_exercise("Squat", "legs")), 0.0)
        with self.assertRaises(InvalidWorkoutException):
            analyzer.best_workout([])
