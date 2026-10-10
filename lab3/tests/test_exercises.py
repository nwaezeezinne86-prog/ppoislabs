import unittest
from datetime import datetime, timedelta

from fitness.exceptions import InvalidWorkoutException, WorkoutNotFoundException
from fitness.exercises import Exercise, Workout, WorkoutPlan, WorkoutSession, WorkoutSet
from fitness.health import HeartRateMonitor, HeartRateReading
from tests.factories import NOW, TODAY, make_device, make_exercise, make_set, make_user, make_workout


class ExerciseTest(unittest.TestCase):
    def test_valid_exercise(self):
        exercise = make_exercise()
        exercise.validate()
        self.assertEqual(exercise.calories_burned(10), 60.0)
        self.assertTrue(exercise.targets("chest"))
        self.assertFalse(exercise.targets("legs"))
        self.assertTrue(Exercise("Burpee", "full body", 10.0, 4).targets("legs"))

    def test_invalid_exercise(self):
        for item in (Exercise("x", "wings", 5.0, 3), Exercise("x", "chest", 0.0, 3), Exercise("x", "chest", 5.0, 9)):
            with self.assertRaises(InvalidWorkoutException):
                item.validate()


class WorkoutSetTest(unittest.TestCase):
    def test_calculations(self):
        workout_set = make_set(10, 50.0)
        self.assertEqual(workout_set.volume(), 500.0)
        self.assertAlmostEqual(workout_set.estimated_one_rep_max(), 66.666, places=2)
        self.assertEqual(workout_set.duration_seconds(), 90)

    def test_validate(self):
        make_set().validate()
        with self.assertRaises(InvalidWorkoutException):
            WorkoutSet(make_exercise(), 0, 10.0, 30).validate()


class WorkoutTest(unittest.TestCase):
    def test_totals(self):
        workout = make_workout()
        workout.validate()
        self.assertEqual(workout.total_volume(), 980.0)
        self.assertEqual(workout.muscle_groups(), {"chest"})
        self.assertEqual(workout.exercise_count(), 1)
        self.assertGreater(workout.calories_burned(), 0)

    def test_invalid_workout(self):
        with self.assertRaises(InvalidWorkoutException):
            Workout(1, "Empty", TODAY, 30).validate()
        with self.assertRaises(InvalidWorkoutException):
            Workout(1, "Empty", TODAY, 30).add_set(WorkoutSet(make_exercise(), 0, 1.0, 1))


class WorkoutPlanTest(unittest.TestCase):
    def test_plan(self):
        plan = WorkoutPlan("Strength", 4)
        self.assertEqual(plan.average_duration(), 0.0)
        plan.add_workout(make_workout())
        self.assertEqual(plan.total_sessions(), 4)
        self.assertEqual(plan.average_duration(), 45.0)
        self.assertEqual(plan.find_workout("Push day").workout_id, 1)
        with self.assertRaises(WorkoutNotFoundException):
            plan.find_workout("Missing")

    def test_invalid_workout_rejected(self):
        with self.assertRaises(InvalidWorkoutException):
            WorkoutPlan("Strength", 4).add_workout(Workout(1, "Empty", TODAY, 30))


class WorkoutSessionTest(unittest.TestCase):
    def test_lifecycle(self):
        session = WorkoutSession(make_workout(), make_user())
        self.assertEqual(session.elapsed_minutes(), 0.0)
        session.begin(NOW)
        with self.assertRaises(InvalidWorkoutException):
            session.begin(NOW)
        session.finish(NOW + timedelta(minutes=45))
        self.assertTrue(session.is_finished())
        self.assertEqual(session.elapsed_minutes(), 45.0)

    def test_finish_errors(self):
        session = WorkoutSession(make_workout(), make_user())
        with self.assertRaises(InvalidWorkoutException):
            session.finish(NOW)
        session.begin(NOW)
        with self.assertRaises(InvalidWorkoutException):
            session.finish(NOW - timedelta(minutes=1))

    def test_heart_rate(self):
        session = WorkoutSession(make_workout(), make_user())
        self.assertEqual(session.average_heart_rate(), 0.0)
        monitor = HeartRateMonitor(make_device())
        monitor.record(HeartRateReading(120, datetime(2026, 10, 10, 9, 1)))
        session.monitor = monitor
        self.assertEqual(session.average_heart_rate(), 120.0)
