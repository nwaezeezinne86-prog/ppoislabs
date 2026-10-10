import unittest
from datetime import datetime

from fitness.activities import CardioActivity, Cycling, GPSPoint, Route, Running, Swimming
from fitness.exceptions import InvalidMeasurementException, InvalidWorkoutException
from tests.factories import NOW, make_user

LATER = datetime(2026, 10, 10, 9, 30)


def point(lat: float, lon: float, alt: float = 0.0) -> GPSPoint:
    return GPSPoint(lat, lon, alt, NOW)


class GPSPointTest(unittest.TestCase):
    def test_distance(self):
        self.assertAlmostEqual(point(0, 0).distance_to(point(0, 1)), 111.19, places=1)
        self.assertEqual(point(10, 10).distance_to(point(10, 10)), 0.0)

    def test_elevation_and_validation(self):
        self.assertEqual(point(0, 0, 10).elevation_change(point(0, 1, 25)), 15)
        point(0, 0).validate()
        for bad in (point(91, 0), point(0, 181)):
            with self.assertRaises(InvalidMeasurementException):
                bad.validate()


class RouteTest(unittest.TestCase):
    def test_route(self):
        route = Route("Park loop")
        route.add_point(point(0, 0, 0))
        route.add_point(point(0, 0.01, 20))
        route.add_point(point(0, 0.02, 5))
        self.assertEqual(route.point_count(), 3)
        self.assertAlmostEqual(route.total_distance_km(), 2.224, places=2)
        self.assertEqual(route.elevation_gain_m(), 20)

    def test_invalid_point(self):
        with self.assertRaises(InvalidMeasurementException):
            Route("Bad").add_point(point(100, 0))


class CardioActivityTest(unittest.TestCase):
    def test_metrics(self):
        activity = CardioActivity(1, make_user(), NOW, 30.0, 5.0)
        activity.validate()
        self.assertEqual(activity.average_speed_kmh(), 10.0)
        self.assertEqual(activity.pace_min_per_km(), 6.0)
        self.assertGreater(activity.calories_burned(), 0)
        self.assertEqual(activity.intensity_met(), 9.8)

    def test_invalid(self):
        for activity in (CardioActivity(1, make_user(), NOW, 0.0, 5.0), CardioActivity(1, make_user(), NOW, 10.0, -1.0)):
            with self.assertRaises(InvalidWorkoutException):
                activity.validate()
        with self.assertRaises(InvalidWorkoutException):
            CardioActivity(1, make_user(), NOW, 10.0, 0.0).pace_min_per_km()


class SubclassTest(unittest.TestCase):
    def test_running(self):
        run = Running(1, make_user(), NOW, 30.0, 5.0, cadence_spm=170)
        self.assertEqual(run.estimated_steps(), 5100)
        self.assertEqual(run.intensity_met(), 9.8)

    def test_cycling(self):
        ride = Cycling(1, make_user(), NOW, 60.0, 20.0, elevation_gain_m=200.0)
        self.assertEqual(ride.climbing_ratio(), 0.01)
        self.assertEqual(ride.intensity_met(), 7.5)
        self.assertEqual(Cycling(1, make_user(), NOW, 60.0, 0.0).climbing_ratio(), 0.0)

    def test_swimming(self):
        swim = Swimming(1, make_user(), NOW, 40.0, 1.0, laps=40, pool_length_m=25.0)
        self.assertEqual(swim.pool_distance_km(), 1.0)
        self.assertEqual(swim.laps_per_minute(), 1.0)
        self.assertEqual(swim.intensity_met(), 8.0)
