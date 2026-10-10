import unittest
from datetime import date, datetime, timedelta

from fitness.activities import Running
from fitness.app import FitnessApp
from fitness.exceptions import (
    AuthenticationException, DuplicateEntryException, InvalidUserDataException, InvalidWorkoutException,
)
from fitness.goals import Goal
from fitness.nutrition import Food, Meal
from fitness.social import Challenge
from tests.factories import NOW, PASSWORD, TODAY, make_profile, make_workout

BIRTH = date(1995, 5, 20)


def register(app: FitnessApp, name: str = "Alex"):
    return app.register_user(name, f"{name.lower()}@mail.com", BIRTH, PASSWORD, make_profile(), NOW)


class RegistrationTest(unittest.TestCase):
    def test_register_and_find(self):
        app = FitnessApp()
        alex, bob = register(app), register(app, "Bob")
        self.assertEqual((alex.user_id, bob.user_id), (1, 2))
        self.assertEqual(app.find_user(2), bob)
        self.assertEqual(app.find_by_email("alex@mail.com"), alex)
        self.assertIsNone(app.find_by_email("nobody@mail.com"))

    def test_errors(self):
        app = FitnessApp()
        register(app)
        with self.assertRaises(DuplicateEntryException):
            register(app)
        with self.assertRaises(InvalidUserDataException):
            app.find_user(99)
        with self.assertRaises(InvalidUserDataException):
            app.register_user("A", "a@mail.com", BIRTH, PASSWORD, make_profile(), NOW)

    def test_login(self):
        app = FitnessApp()
        alex = register(app)
        self.assertEqual(app.login("alex@mail.com", PASSWORD), alex)
        with self.assertRaises(AuthenticationException):
            app.login("alex@mail.com", "wrong123")
        with self.assertRaises(AuthenticationException):
            app.login("ghost@mail.com", PASSWORD)


class LoggingTest(unittest.TestCase):
    def setUp(self):
        self.app = FitnessApp()
        self.user = register(self.app)

    def test_workout_updates_streak_and_notifies(self):
        self.app.log_workout(self.user, make_workout(), NOW)
        self.assertEqual(len(self.app.workouts[1]), 1)
        self.assertEqual(self.app.achievements[1].streak.current_days, 1)
        self.assertEqual(len(self.app.notifications.unread_for(self.user)), 1)

    def test_invalid_workout(self):
        from fitness.exercises import Workout
        with self.assertRaises(InvalidWorkoutException):
            self.app.log_workout(self.user, Workout(1, "Empty", TODAY, 10), NOW)

    def test_activity_meal_goal(self):
        run = Running(1, self.user, NOW, 30.0, 5.0)
        self.app.log_activity(self.user, run, NOW)
        self.app.log_meal(self.user, Meal("lunch", NOW, [Food("Egg", 80.0, 6.0, 1.0, 5.0)]))
        self.app.add_goal(self.user, Goal(1, "Run", 10.0, TODAY + timedelta(days=5), self.user), TODAY)
        self.assertEqual(self.app.nutrition_logs[1].calories_on(TODAY), 80.0)
        self.assertEqual(len(self.app.achievements[1].goals), 1)

    def test_weekly_report_filters_by_period(self):
        self.app.log_workout(self.user, make_workout(1, TODAY), NOW)
        self.app.log_workout(self.user, make_workout(2, TODAY - timedelta(days=30)), NOW)
        self.app.log_activity(self.user, Running(1, self.user, NOW, 30.0, 5.0), NOW)
        report = self.app.weekly_report(self.user, TODAY - timedelta(days=7), TODAY)
        self.assertEqual(report.total_workouts(), 2)

    def test_challenges_and_posts(self):
        challenge = Challenge("Steps", TODAY, TODAY + timedelta(days=7))
        self.app.create_challenge(challenge)
        with self.assertRaises(DuplicateEntryException):
            self.app.create_challenge(challenge)
        self.app.join_challenge("Steps", self.user)
        self.assertEqual(len(self.app.leaderboard("Steps").ranking()), 1)
        with self.assertRaises(InvalidUserDataException):
            self.app.get_challenge("Missing")
        post = self.app.share_post(self.user, "Hello", datetime(2026, 10, 10, 10, 0))
        self.assertEqual(self.app.feed.posts, [post])
