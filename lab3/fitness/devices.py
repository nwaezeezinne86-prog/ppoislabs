"""Wearable devices, notifications and reminders."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .constants import (
    DEFAULT_SNOOZE_MINUTES, FULL_BATTERY_PERCENT, LOW_BATTERY_PERCENT, SYNC_BATTERY_COST,
)
from .exceptions import DeviceNotConnectedException, InvalidContentException

if TYPE_CHECKING:
    from .users import User


@dataclass
class Device:
    """A wearable tracker owned by a user."""

    device_id: int
    model: str
    owner: User
    battery_percent: int = FULL_BATTERY_PERCENT
    connected: bool = False

    def connect(self) -> None:
        if self.battery_percent > 0:
            self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def require_connected(self) -> None:
        if not self.connected:
            raise DeviceNotConnectedException(f"Device {self.model} is not connected")

    def drain(self, amount: int) -> None:
        self.battery_percent = max(self.battery_percent - amount, 0)
        if self.battery_percent == 0:
            self.connected = False

    def charge(self) -> None:
        self.battery_percent = FULL_BATTERY_PERCENT

    def needs_charging(self) -> bool:
        return self.battery_percent <= LOW_BATTERY_PERCENT


@dataclass
class DeviceSyncService:
    """Synchronises all registered devices."""

    devices: list[Device] = field(default_factory=list)
    last_sync: datetime | None = None

    def register(self, device: Device) -> None:
        self.devices.append(device)

    def connected_devices(self) -> list[Device]:
        return [device for device in self.devices if device.connected]

    def low_battery_devices(self) -> list[Device]:
        return [device for device in self.devices if device.needs_charging()]

    def sync_all(self, now: datetime) -> int:
        synced = self.connected_devices()
        for device in synced:
            device.drain(SYNC_BATTERY_COST)
        self.last_sync = now
        return len(synced)


@dataclass
class Notification:
    """A message addressed to a user."""

    user: User
    message: str
    created_at: datetime
    read: bool = False

    def mark_read(self) -> None:
        self.read = True

    def is_unread(self) -> bool:
        return not self.read


@dataclass
class NotificationService:
    """Stores and delivers notifications."""

    queue: list[Notification] = field(default_factory=list)

    def send(self, user: User, message: str, now: datetime) -> Notification:
        if not message.strip():
            raise InvalidContentException("Notification text is empty")
        notification = Notification(user, message, now)
        self.queue.append(notification)
        return notification

    def unread_for(self, user: User) -> list[Notification]:
        return [item for item in self.queue if item.user.user_id == user.user_id and item.is_unread()]

    def mark_all_read(self, user: User) -> int:
        unread = self.unread_for(user)
        for item in unread:
            item.mark_read()
        return len(unread)


@dataclass
class Reminder:
    """A scheduled reminder for a workout or meal."""

    user: User
    message: str
    remind_at: datetime
    repeat_daily: bool = False

    def is_due(self, now: datetime) -> bool:
        return now >= self.remind_at

    def next_occurrence(self) -> datetime | None:
        return self.remind_at + timedelta(days=1) if self.repeat_daily else None

    def snooze(self, minutes: int = DEFAULT_SNOOZE_MINUTES) -> None:
        self.remind_at += timedelta(minutes=minutes)

    def advance(self) -> bool:
        following = self.next_occurrence()
        if following is None:
            return False
        self.remind_at = following
        return True
