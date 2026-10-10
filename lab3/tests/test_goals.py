import unittest
from datetime import date, timedelta

from fitness.exceptions import DuplicateEntryException, GoalNotAchievableException
from fitness.goals import AchievementManager, Badge, DistanceGoal, Goal, Streak, WeightGoal, WorkoutFrequencyGoal
from tests.factories import TODAY, make_user

DEADLINE = TODAY + timedelta(days=28)


def weight_goal(start: float, target: float, current: float) -> WeightGoal:
    return WeightGoal(1, "Weight", target, DEADLINE, make_user(), current, start)


class GoalTest(unittest.TestCase):
    def test_progress(self):
        goal = Goal(1, "Steps", 200.0, DEADLINE, make_user())
        goal.validate(TODAY)
        goal.update_progress(50.0)
        self.assertEqual(goal.progress_percent(), 25.0)
        self.assertFalse(goal.is_achieved())
        self.assertEqual(goal.days_remaining(TODAY), 28)
        goal.update_progress(300.0)
        self.assertEqual(goal.progress_percent(), 100.0)
        self.assertTrue(goal.is_achieved())

    def test_overdue(self):
        goal = Goal(1, "Steps", 200.0, DEADLINE, make_user())
        self.assertFalse(goal.is_overdue(TODAY))
        self.assertTrue(goal.is_overdue(DEADLINE + timedelta(days=1)))

    def test_invalid(self):
        with self.assertRaises(GoalNotAchievableException):
            Goal(1, "Bad", 0.0, DEADLINE, make_user()).validate(TODAY)
        with self.assertRaises(GoalNotAchievableException):
            Goal(1, "Late", 10.0, TODAY - timedelta(days=1), make_user()).validate(TODAY)


class WeightGoalTest(unittest.TestCase):
    def test_loss(self):
        goal = weight_goal(90.0, 80.0, 85.0)
        goal.validate(TODAY)
        self.assertEqual(goal.progress_percent(), 50.0)
        self.assertFalse(goal.is_achieved())
        self.assertEqual(goal.required_weekly_change(TODAY), -1.25)
        goal.update_progress(79.0)
        self.assertTrue(goal.is_achieved())
        self.assertEqual(goal.progress_percent(), 100.0)

    def test_gain(self):
        goal = weight_goal(60.0, 70.0, 65.0)
        self.assertEqual(goal.progress_percent(), 50.0)
        goal.update_progress(71.0)
        self.assertTrue(goal.is_achieved())

    def test_wrong_direction_progress_is_zero(self):
        self.assertEqual(weight_goal(90.0, 80.0, 95.0).progress_percent(), 0.0)

    def test_invalid(self):
        with self.assertRaises(GoalNotAchievableException):
            weight_goal(80.0, 80.0, 80.0).validate(TODAY)
        with self.assertRaises(GoalNotAchievableException):
            weight_goal(90.0, 80.0, 85.0).required_weekly_change(DEADLINE)


class OtherGoalsTest(unittest.TestCase):
    def test_distance_goal(self):
        goal = DistanceGoal(1, "Run", 100.0, DEADLINE, make_user())
        goal.add_distance(30.0)
        self.assertEqual(goal.remaining_km(), 70.0)
        goal.add_distance(100.0)
        self.assertEqual(goal.remaining_km(), 0.0)
        with self.assertRaises(GoalNotAchievableException):
            goal.add_distance(-1.0)

    def test_frequency_goal(self):
        goal = WorkoutFrequencyGoal(1, "Gym", 12.0, DEADLINE, make_user(), sessions_per_week=3)
        self.assertFalse(goal.is_on_track(1))
        for _ in range(3):
            goal.register_workout()
        self.assertTrue(goal.is_on_track(1))
        self.assertFalse(goal.is_on_track(2))


class BadgeStreakTest(unittest.TestCase):
    def test_badge(self):
        badge = Badge("First run", "Complete a run", 10)
        self.assertFalse(badge.is_earned())
        badge.award(TODAY)
        self.assertTrue(badge.is_earned())
        with self.assertRaises(DuplicateEntryException):
            badge.award(TODAY)

    def test_streak(self):
        streak = Streak()
        self.assertFalse(streak.is_active(TODAY))
        streak.record_activity(TODAY)
        streak.record_activity(TODAY)
        streak.record_activity(TODAY + timedelta(days=1))
        self.assertEqual((streak.current_days, streak.longest_days), (2, 2))
        streak.record_activity(TODAY + timedelta(days=5))
        self.assertEqual((streak.current_days, streak.longest_days), (1, 2))
        self.assertTrue(streak.is_active(TODAY + timedelta(days=6)))
        self.assertFalse(streak.is_active(TODAY + timedelta(days=9)))
        streak.reset()
        self.assertEqual(streak.current_days, 0)


class AchievementManagerTest(unittest.TestCase):
    def test_manager(self):
        user = make_user()
        manager = AchievementManager(user)
        done = Goal(1, "Done", 10.0, DEADLINE, user, 10.0)
        late = Goal(2, "Late", 10.0, TODAY, user, 1.0)
        manager.add_goal(done, TODAY)
        manager.add_goal(late, TODAY)
        manager.award_badge(Badge("A", "a", 10), TODAY)
        manager.award_badge(Badge("B", "b", 15), TODAY)
        self.assertEqual(manager.total_points(), 25)
        self.assertEqual(manager.achieved_goals(), [done])
        self.assertEqual(manager.overdue_goals(TODAY + timedelta(days=1)), [late])

    def test_invalid_goal(self):
        manager = AchievementManager(make_user())
        with self.assertRaises(GoalNotAchievableException):
            manager.add_goal(Goal(1, "Bad", -1.0, DEADLINE, make_user()), date(2026, 10, 10))
