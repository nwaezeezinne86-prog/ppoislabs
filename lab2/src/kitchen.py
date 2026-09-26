"""Kitchen operations: workstations, tasks, task queues."""
from __future__ import annotations

from datetime import datetime, timedelta

from .equipment import Equipment
from .exceptions import EquipmentUnavailableError, InvalidScheduleError
from .people import Cook


class KitchenTask:
    """A single task to be performed at a workstation."""

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"

    def __init__(
        self,
        name: str,
        minutes: int,
        assigned_cook: Cook | None = None,
    ) -> None:
        if minutes <= 0:
            raise InvalidScheduleError("Task duration must be positive")
        self._name = name
        self._minutes = minutes
        self._assigned_cook = assigned_cook
        self._status = self.STATUS_PENDING
        self._started_at: datetime | None = None
        self._finished_at: datetime | None = None

    @property
    def name(self) -> str:
        """Task name."""
        return self._name

    @property
    def minutes(self) -> int:
        """Planned duration in minutes."""
        return self._minutes

    @property
    def status(self) -> str:
        """Current status."""
        return self._status

    @property
    def assigned_cook(self) -> Cook | None:
        """Cook assigned to the task, if any."""
        return self._assigned_cook

    def assign_to(self, cook: Cook) -> None:
        """Assign the task to a cook."""
        self._assigned_cook = cook

    def start(self, now: datetime) -> None:
        """Start the task."""
        if self._status != self.STATUS_PENDING:
            raise InvalidScheduleError(
                f"Task {self._name} is not pending (status={self._status})"
            )
        self._status = self.STATUS_RUNNING
        self._started_at = now

    def finish(self, now: datetime) -> None:
        """Mark the task as done."""
        if self._status != self.STATUS_RUNNING:
            raise InvalidScheduleError(
                f"Task {self._name} is not running (status={self._status})"
            )
        self._status = self.STATUS_DONE
        self._finished_at = now

    def fail(self, reason: str = "") -> None:
        """Mark the task as failed."""
        self._status = self.STATUS_FAILED
        self._name = f"{self._name} [{reason}]" if reason else self._name

    def actual_duration(self) -> timedelta | None:
        """Return the actual duration if the task has finished."""
        if self._started_at is None or self._finished_at is None:
            return None
        return self._finished_at - self._started_at

    def describe(self) -> str:
        cook_name = self._assigned_cook.full_name() if self._assigned_cook else "unassigned"
        return (
            f"Task '{self._name}' ({self._minutes} min, {cook_name}, "
            f"status={self._status})"
        )


class Workstation:
    """A cooking station with equipment and an assigned cook."""

    def __init__(self, name: str, purpose: str, equipment: Equipment | None = None) -> None:
        self._name = name
        self._purpose = purpose
        self._equipment = equipment
        self._assigned_cook: Cook | None = None
        self._tasks: list[KitchenTask] = []

    @property
    def name(self) -> str:
        """Workstation name."""
        return self._name

    @property
    def purpose(self) -> str:
        """What this station is used for."""
        return self._purpose

    @property
    def equipment(self) -> Equipment | None:
        """Equipment mounted on this station."""
        return self._equipment

    def assign_cook(self, cook: Cook) -> None:
        """Assign a cook to this station."""
        self._assigned_cook = cook

    def unassign_cook(self) -> None:
        """Clear the assigned cook."""
        self._assigned_cook = None

    def queue_task(self, task: KitchenTask) -> None:
        """Queue a task at this station."""
        self._tasks.append(task)

    def pop_next(self) -> KitchenTask | None:
        """Return the next pending task or None."""
        for task in self._tasks:
            if task.status == KitchenTask.STATUS_PENDING:
                return task
        return None

    def task_count(self) -> int:
        """Return the total number of queued tasks."""
        return len(self._tasks)

    def pending_count(self) -> int:
        """Return how many tasks are still pending."""
        return sum(
            1 for t in self._tasks
            if t.status == KitchenTask.STATUS_PENDING
        )

    def acquire_equipment(self) -> None:
        """Acquire this station's equipment."""
        if self._equipment is None:
            raise EquipmentUnavailableError(
                f"Station {self._name} has no equipment"
            )
        self._equipment.acquire()

    def release_equipment(self) -> None:
        """Release this station's equipment."""
        if self._equipment is not None:
            self._equipment.release()

    def describe(self) -> str:
        cook_name = self._assigned_cook.full_name() if self._assigned_cook else "unassigned"
        eq = self._equipment.name if self._equipment else "no equipment"
        return (
            f"Workstation '{self._name}' for {self._purpose} "
            f"({cook_name}, {eq}, {self.task_count()} tasks)"
        )


class Kitchen:
    """The kitchen itself: stations and a running queue of tasks."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._stations: list[Workstation] = []

    @property
    def name(self) -> str:
        """Kitchen name."""
        return self._name

    def add_station(self, station: Workstation) -> None:
        """Add a station to the kitchen."""
        self._stations.append(station)

    def remove_station(self, name: str) -> None:
        """Remove a station by name."""
        self._stations = [s for s in self._stations if s.name != name]

    def find_station(self, name: str) -> Workstation | None:
        """Return a station by name or None."""
        for s in self._stations:
            if s.name == name:
                return s
        return None

    def station_count(self) -> int:
        """Return the number of stations."""
        return len(self._stations)

    def total_pending_tasks(self) -> int:
        """Return the total number of pending tasks across all stations."""
        return sum(s.pending_count() for s in self._stations)

    def all_tasks(self) -> list[KitchenTask]:
        """Return all tasks across all stations."""
        result: list[KitchenTask] = []
        for s in self._stations:
            result.extend(s._tasks)
        return result

    def find_task(self, name: str) -> KitchenTask | None:
        """Return the first task with a matching name or None."""
        for task in self.all_tasks():
            if task.name == name:
                return task
        return None

    def describe(self) -> str:
        return (
            f"Kitchen '{self._name}' "
            f"({self.station_count()} stations, "
            f"{self.total_pending_tasks()} pending tasks)"
        )


class ShiftHandover:
    """Record of a kitchen shift handover between two cooks."""

    def __init__(
        self,
        kitchen: Kitchen,
        outgoing: Cook,
        incoming: Cook,
        when: datetime,
    ) -> None:
        if outgoing == incoming:
            raise InvalidScheduleError("Handover requires two distinct cooks")
        self._kitchen = kitchen
        self._outgoing = outgoing
        self._incoming = incoming
        self._when = when
        self._notes: list[str] = []

    @property
    def when(self) -> datetime:
        """Handover timestamp."""
        return self._when

    def add_note(self, note: str) -> None:
        """Add a note for the incoming cook."""
        self._notes.append(note)

    def note_count(self) -> int:
        """Return the number of notes."""
        return len(self._notes)

    def describe(self) -> str:
        return (
            f"Handover from {self._outgoing.full_name()} to "
            f"{self._incoming.full_name()} at {self._when:%Y-%m-%d %H:%M} "
            f"({self.note_count()} notes)"
        )
