import unittest
from datetime import timedelta

from fitness.exceptions import DeviceNotConnectedException, InvalidMeasurementException
from fitness.health import (
    HeartRateMonitor, HeartRateReading, HeartRateZone, HydrationEntry, HydrationLog, SleepRecord, StepCounter,
)
from tests.factories import NOW, TODAY, make_device, make_user


def reading(bpm: int) -> HeartRateReading:
    return HeartRateReading(bpm, NOW)


class HeartRateTest(unittest.TestCase):
    def test_reading_validation(self):
        reading(80).validate()
        with self.assertRaises(InvalidMeasurementException):
            reading(10).validate()

    def test_zone_contains(self):
        zone = HeartRateZone("cardio", 120, 150)
        self.assertTrue(zone.contains(120))
        self.assertFalse(zone.contains(151))

    def test_zones_for_age(self):
        zones = HeartRateMonitor.zones_for_age(30)
        self.assertEqual(len(zones), 4)
        self.assertEqual(zones[-1].max_bpm, 190)

    def test_monitor_statistics(self):
        monitor = HeartRateMonitor(make_device(), zones=HeartRateMonitor.zones_for_age(30))
        self.assertEqual((monitor.average_bpm(), monitor.peak_bpm(), monitor.resting_bpm()), (0.0, 0, 0))
        for bpm in (60, 100, 170):
            monitor.record(reading(bpm))
        self.assertEqual(monitor.average_bpm(), 110.0)
        self.assertEqual((monitor.peak_bpm(), monitor.resting_bpm()), (170, 60))
        zone = monitor.zone_for(170)
        self.assertEqual(zone.name, "peak")
        self.assertEqual(monitor.readings_in_zone(zone), 1)
        self.assertIsNone(monitor.zone_for(20))

    def test_disconnected_device(self):
        monitor = HeartRateMonitor(make_device(connected=False))
        with self.assertRaises(DeviceNotConnectedException):
            monitor.record(reading(80))


class SleepRecordTest(unittest.TestCase):
    def test_metrics(self):
        record = SleepRecord(make_user(), NOW, NOW + timedelta(hours=8), 85)
        record.validate()
        self.assertEqual(record.duration_hours(), 8.0)
        self.assertTrue(record.is_sufficient())
        self.assertEqual(record.quality_label(), "good")

    def test_labels(self):
        user = make_user()
        self.assertEqual(SleepRecord(user, NOW, NOW + timedelta(hours=5), 60).quality_label(), "fair")
        self.assertEqual(SleepRecord(user, NOW, NOW + timedelta(hours=5), 10).quality_label(), "poor")
        self.assertFalse(SleepRecord(user, NOW, NOW + timedelta(hours=5), 10).is_sufficient())

    def test_invalid(self):
        user = make_user()
        for record in (SleepRecord(user, NOW, NOW, 50), SleepRecord(user, NOW, NOW + timedelta(hours=8), 150)):
            with self.assertRaises(InvalidMeasurementException):
                record.validate()


class StepCounterTest(unittest.TestCase):
    def test_steps(self):
        counter = StepCounter(daily_goal=1000)
        counter.add_steps(TODAY, 600)
        counter.add_steps(TODAY, 600)
        counter.add_steps(TODAY - timedelta(days=2), 100)
        self.assertEqual(counter.steps_on(TODAY), 1200)
        self.assertTrue(counter.goal_reached(TODAY))
        self.assertFalse(counter.goal_reached(TODAY - timedelta(days=2)))
        self.assertEqual(counter.weekly_total(TODAY), 1300)
        self.assertAlmostEqual(counter.distance_km(TODAY), 0.9144)

    def test_negative_steps(self):
        with self.assertRaises(InvalidMeasurementException):
            StepCounter().add_steps(TODAY, -1)


class HydrationTest(unittest.TestCase):
    def test_log(self):
        log = HydrationLog(daily_goal_ml=1000)
        log.add_entry(HydrationEntry(400, NOW))
        log.add_entry(HydrationEntry(300, NOW))
        log.add_entry(HydrationEntry(500, NOW - timedelta(days=1)))
        self.assertEqual(log.total_on(TODAY), 700)
        self.assertEqual(log.remaining_on(TODAY), 300)
        self.assertFalse(log.goal_reached(TODAY))
        log.add_entry(HydrationEntry(300, NOW))
        self.assertTrue(log.goal_reached(TODAY))
        self.assertEqual(log.remaining_on(TODAY), 0)

    def test_invalid_entry(self):
        with self.assertRaises(InvalidMeasurementException):
            HydrationLog().add_entry(HydrationEntry(0, NOW))
