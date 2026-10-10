import unittest
from datetime import timedelta

from fitness.coaching import Trainer, TrainingSession
from fitness.devices import Device, DeviceSyncService, Notification, NotificationService, Reminder
from fitness.exceptions import (
    DeviceNotConnectedException, DuplicateEntryException, InvalidContentException, InvalidUserDataException,
    SubscriptionRequiredException, TrainerNotAvailableException,
)
from tests.factories import NOW, make_device, make_subscription, make_user


def make_trainer() -> Trainer:
    return Trainer(1, "Coach", "strength", 40.0)


class TrainerTest(unittest.TestCase):
    def test_clients(self):
        trainer, user = make_trainer(), make_user()
        trainer.accept_client(user)
        self.assertTrue(trainer.has_client(user))
        with self.assertRaises(DuplicateEntryException):
            trainer.accept_client(user)
        trainer.release_client(user)
        self.assertFalse(trainer.has_client(user))
        with self.assertRaises(InvalidUserDataException):
            trainer.release_client(user)

    def test_availability_and_cost(self):
        trainer = make_trainer()
        self.assertEqual(trainer.session_cost(1.5), 60.0)
        trainer.pause()
        with self.assertRaises(TrainerNotAvailableException):
            trainer.accept_client(make_user())
        trainer.resume()
        self.assertTrue(trainer.is_available)


class TrainingSessionTest(unittest.TestCase):
    def make_session(self, coaching: bool = True) -> TrainingSession:
        client = make_user()
        client.subscribe(make_subscription(coaching))
        return TrainingSession(make_trainer(), client, NOW + timedelta(days=1), 90)

    def test_flow(self):
        session = self.make_session()
        self.assertTrue(session.is_upcoming(NOW))
        with self.assertRaises(InvalidUserDataException):
            session.complete()
        session.confirm()
        session.complete()
        self.assertEqual(session.status, "completed")
        self.assertEqual(session.cost(), 60.0)

    def test_cancel(self):
        session = self.make_session()
        session.cancel()
        self.assertFalse(session.is_upcoming(NOW))

    def test_confirm_errors(self):
        with self.assertRaises(SubscriptionRequiredException):
            self.make_session(coaching=False).confirm()
        session = TrainingSession(make_trainer(), make_user(), NOW, 60)
        with self.assertRaises(SubscriptionRequiredException):
            session.confirm()
        session.trainer.pause()
        with self.assertRaises(TrainerNotAvailableException):
            session.confirm()


class DeviceTest(unittest.TestCase):
    def test_connection(self):
        device = make_device(connected=False)
        with self.assertRaises(DeviceNotConnectedException):
            device.require_connected()
        device.connect()
        device.require_connected()
        device.disconnect()
        self.assertFalse(device.connected)

    def test_battery(self):
        device = make_device()
        device.drain(85)
        self.assertTrue(device.needs_charging())
        device.drain(50)
        self.assertEqual(device.battery_percent, 0)
        self.assertFalse(device.connected)
        device.connect()
        self.assertFalse(device.connected)
        device.charge()
        device.connect()
        self.assertTrue(device.connected)


class SyncServiceTest(unittest.TestCase):
    def test_sync(self):
        service = DeviceSyncService()
        online, offline = make_device(), make_device(connected=False)
        low = Device(3, "Old", make_user(), battery_percent=10)
        for device in (online, offline, low):
            service.register(device)
        self.assertEqual(service.connected_devices(), [online])
        self.assertEqual(service.low_battery_devices(), [low])
        self.assertEqual(service.sync_all(NOW), 1)
        self.assertEqual(service.last_sync, NOW)
        self.assertEqual(online.battery_percent, 98)


class NotificationTest(unittest.TestCase):
    def test_notification(self):
        notification = Notification(make_user(), "Hi", NOW)
        self.assertTrue(notification.is_unread())
        notification.mark_read()
        self.assertFalse(notification.is_unread())

    def test_service(self):
        service, alex, bob = NotificationService(), make_user(1, "Alex"), make_user(2, "Bob")
        service.send(alex, "One", NOW)
        service.send(alex, "Two", NOW)
        service.send(bob, "Three", NOW)
        self.assertEqual(len(service.unread_for(alex)), 2)
        self.assertEqual(service.mark_all_read(alex), 2)
        self.assertEqual(service.unread_for(alex), [])
        with self.assertRaises(InvalidContentException):
            service.send(alex, "  ", NOW)


class ReminderTest(unittest.TestCase):
    def test_due_and_snooze(self):
        reminder = Reminder(make_user(), "Train", NOW)
        self.assertTrue(reminder.is_due(NOW))
        reminder.snooze()
        self.assertFalse(reminder.is_due(NOW))
        self.assertEqual(reminder.remind_at, NOW + timedelta(minutes=10))

    def test_repeat(self):
        daily = Reminder(make_user(), "Water", NOW, repeat_daily=True)
        self.assertEqual(daily.next_occurrence(), NOW + timedelta(days=1))
        self.assertTrue(daily.advance())
        self.assertEqual(daily.remind_at, NOW + timedelta(days=1))
        once = Reminder(make_user(), "Once", NOW)
        self.assertIsNone(once.next_occurrence())
        self.assertFalse(once.advance())
