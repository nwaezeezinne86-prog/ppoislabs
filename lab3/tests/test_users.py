import unittest
from datetime import date, datetime

from fitness.exceptions import (
    AuthenticationException, InvalidMeasurementException, InvalidUserDataException, SubscriptionRequiredException,
)
from fitness.users import Account, BodyMeasurement, Subscription, UserProfile
from tests.factories import NOW, PASSWORD, TODAY, make_plan, make_profile, make_subscription, make_user


class UserProfileTest(unittest.TestCase):
    def test_valid_profile(self):
        profile = make_profile()
        profile.validate()
        self.assertEqual(profile.height_m(), 1.8)
        self.assertEqual(profile.activity_multiplier(), 1.55)

    def test_invalid_values(self):
        bad_profiles = [UserProfile(10, 80, "male"), UserProfile(180, 5, "male"),
                        UserProfile(180, 80, "other"), UserProfile(180, 80, "male", "lazy")]
        for profile in bad_profiles:
            with self.assertRaises(InvalidUserDataException):
                profile.validate()

    def test_update_weight(self):
        profile = make_profile()
        profile.update_weight(75.0)
        self.assertEqual(profile.weight_kg, 75.0)
        with self.assertRaises(InvalidMeasurementException):
            profile.update_weight(1.0)


class AccountTest(unittest.TestCase):
    def test_create_and_check_password(self):
        account = Account.create("a@b.com", PASSWORD, NOW)
        self.assertTrue(account.check_password(PASSWORD))
        self.assertFalse(account.check_password("wrong123"))
        account.authenticate(PASSWORD)

    def test_weak_password_rejected(self):
        for password in ("short1", "onlyletters", "12345678"):
            with self.assertRaises(InvalidUserDataException):
                Account.create("a@b.com", password, NOW)

    def test_authenticate_failures(self):
        account = Account.create("a@b.com", PASSWORD, NOW)
        with self.assertRaises(AuthenticationException):
            account.authenticate("bad")
        account.deactivate()
        with self.assertRaises(AuthenticationException):
            account.authenticate(PASSWORD)

    def test_change_password(self):
        account = Account.create("a@b.com", PASSWORD, NOW)
        account.change_password(PASSWORD, "newpass456")
        self.assertTrue(account.check_password("newpass456"))
        with self.assertRaises(InvalidUserDataException):
            account.change_password("newpass456", "weak")


class BodyMeasurementTest(unittest.TestCase):
    def test_masses(self):
        measurement = BodyMeasurement(TODAY, 80.0, 20.0, 85.0)
        measurement.validate()
        self.assertEqual(measurement.fat_mass_kg(), 16.0)
        self.assertEqual(measurement.lean_mass_kg(), 64.0)

    def test_invalid(self):
        for item in (BodyMeasurement(TODAY, 1.0, 20.0, 85.0), BodyMeasurement(TODAY, 80.0, 99.0, 85.0),
                     BodyMeasurement(TODAY, 80.0, 20.0, 0.0)):
            with self.assertRaises(InvalidMeasurementException):
                item.validate()


class SubscriptionTest(unittest.TestCase):
    def test_plan(self):
        plan = make_plan()
        self.assertAlmostEqual(plan.total_price(3), 29.97)
        self.assertTrue(plan.allows_coaching())
        self.assertTrue(plan.allows_challenges(2))
        self.assertFalse(plan.allows_challenges(3))
        with self.assertRaises(InvalidUserDataException):
            plan.total_price(0)

    def test_subscription_lifecycle(self):
        subscription = make_subscription()
        self.assertTrue(subscription.is_active(TODAY))
        self.assertEqual(subscription.days_left(TODAY), 21)
        subscription.ensure_active(TODAY)
        subscription.renew(1)
        self.assertEqual(subscription.end_date, date(2026, 11, 30))
        subscription.auto_renew = True
        subscription.cancel_auto_renew()
        self.assertFalse(subscription.auto_renew)
        with self.assertRaises(InvalidUserDataException):
            subscription.renew(0)

    def test_expired(self):
        subscription = Subscription(make_plan(), date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(subscription.days_left(TODAY), 0)
        with self.assertRaises(SubscriptionRequiredException):
            subscription.ensure_active(TODAY)


class UserTest(unittest.TestCase):
    def test_validate_and_age(self):
        user = make_user()
        user.validate(TODAY)
        self.assertEqual(user.age(TODAY), 31)
        self.assertEqual(user.age(date(2026, 1, 1)), 30)

    def test_invalid_user(self):
        user = make_user(name="A")
        with self.assertRaises(InvalidUserDataException):
            user.validate(TODAY)
        user = make_user()
        user.email = "bad-email"
        with self.assertRaises(InvalidUserDataException):
            user.validate(TODAY)
        user = make_user()
        user.birth_date = date(2026, 1, 1)
        with self.assertRaises(InvalidUserDataException):
            user.validate(TODAY)

    def test_measurements(self):
        user = make_user()
        self.assertIsNone(user.latest_measurement())
        self.assertEqual(user.weight_change(), 0.0)
        user.record_measurement(BodyMeasurement(TODAY, 80.0, 20.0, 85.0))
        user.record_measurement(BodyMeasurement(TODAY, 77.0, 19.0, 83.0))
        self.assertEqual(user.weight_change(), -3.0)
        self.assertEqual(user.latest_measurement().weight_kg, 77.0)
        self.assertEqual(user.profile.weight_kg, 77.0)

    def test_subscription(self):
        user = make_user()
        self.assertFalse(user.has_active_subscription(TODAY))
        user.subscribe(make_subscription())
        self.assertTrue(user.has_active_subscription(TODAY))
        self.assertFalse(user.has_active_subscription(datetime(2027, 1, 1).date()))
