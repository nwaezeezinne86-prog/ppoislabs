"""Culinary education: schools, courses, lessons, students, certificates."""
from __future__ import annotations

from datetime import date

from .exceptions import (
    CertificateExpiredError,
    InvalidScheduleError,
)
from .money import Money
from .people import Instructor, Student


class Certificate:
    """A certificate awarded to a student."""

    def __init__(self, student: Student, course_name: str, issued_on: date) -> None:
        self._student = student
        self._course_name = course_name
        self._issued_on = issued_on

    @property
    def student(self) -> Student:
        """Student who earned the certificate."""
        return self._student

    @property
    def course_name(self) -> str:
        """Course the certificate is for."""
        return self._course_name

    @property
    def issued_on(self) -> date:
        """Issue date."""
        return self._issued_on

    def age_days(self, today: date) -> int:
        """Return how many days ago the certificate was issued."""
        return (today - self._issued_on).days

    def describe(self) -> str:
        return (
            f"Certificate '{self._course_name}' issued to "
            f"{self._student.full_name()} on {self._issued_on}"
        )


class Lesson:
    """A single lesson in a course."""

    def __init__(
        self,
        title: str,
        scheduled_on: date,
        duration_minutes: int,
        instructor: Instructor,
    ) -> None:
        if duration_minutes <= 0:
            raise ValueError("Lesson duration must be positive")
        self._title = title
        self._scheduled_on = scheduled_on
        self._duration_minutes = duration_minutes
        self._instructor = instructor
        self._attended: list[Student] = []

    @property
    def title(self) -> str:
        """Lesson title."""
        return self._title

    @property
    def scheduled_on(self) -> date:
        """Scheduled date."""
        return self._scheduled_on

    @property
    def instructor(self) -> Instructor:
        """Instructor teaching the lesson."""
        return self._instructor

    def mark_attended(self, student: Student) -> None:
        """Record that a student attended."""
        if student not in self._attended:
            self._attended.append(student)

    def attendance_count(self) -> int:
        """Return the number of attendees."""
        return len(self._attended)

    def describe(self) -> str:
        return (
            f"Lesson '{self._title}' on {self._scheduled_on} "
            f"({self._duration_minutes} min by {self._instructor.full_name()})"
        )


class Course:
    """A course consisting of multiple lessons."""

    def __init__(self, name: str, price: Money, capacity: int = 20) -> None:
        if not name.strip():
            raise ValueError("Course name must not be empty")
        if capacity <= 0:
            raise ValueError("Course capacity must be positive")
        self._name = name
        self._price = price
        self._capacity = capacity
        self._lessons: list[Lesson] = []
        self._enrolled: list[Student] = []

    @property
    def name(self) -> str:
        """Course name."""
        return self._name

    @property
    def price(self) -> Money:
        """Course price."""
        return self._price

    def add_lesson(self, lesson: Lesson) -> None:
        """Add a lesson to the course."""
        self._lessons.append(lesson)

    def enroll(self, student: Student) -> None:
        """Enroll a student; raise if the course is full."""
        if len(self._enrolled) >= self._capacity:
            raise InvalidScheduleError("Course is full")
        if student not in self._enrolled:
            self._enrolled.append(student)

    def enrolled_count(self) -> int:
        """Return the number of enrolled students."""
        return len(self._enrolled)

    def lesson_count(self) -> int:
        """Return the number of lessons."""
        return len(self._lessons)

    def total_minutes(self) -> int:
        """Return the total duration of all lessons."""
        return sum(lesson._duration_minutes for lesson in self._lessons)

    def is_full(self) -> bool:
        """Return True if the course is at capacity."""
        return self.enrolled_count() >= self._capacity

    def describe(self) -> str:
        return (
            f"Course '{self._name}' "
            f"({self.lesson_count()} lessons, "
            f"{self.enrolled_count()}/{self._capacity} enrolled, "
            f"{self._price})"
        )


class CulinarySchool:
    """A culinary school that runs courses and issues certificates."""

    def __init__(self, name: str, address: str) -> None:
        self._name = name
        self._address = address
        self._courses: list[Course] = []
        self._certificates: list[Certificate] = []

    @property
    def name(self) -> str:
        """School name."""
        return self._name

    @property
    def address(self) -> str:
        """School address."""
        return self._address

    def add_course(self, course: Course) -> None:
        """Add a course to the school."""
        self._courses.append(course)

    def find_course(self, name: str) -> Course | None:
        """Return a course by name or None."""
        for c in self._courses:
            if c.name == name:
                return c
        return None

    def award_certificate(
        self,
        student: Student,
        course_name: str,
        issued_on: date,
    ) -> Certificate:
        """Award a certificate; the student must have enrolled in the course."""
        course = self.find_course(course_name)
        if course is None or student not in course._enrolled:
            raise CertificateExpiredError("Student is not enrolled in the course")
        cert = Certificate(student, course_name, issued_on)
        self._certificates.append(cert)
        student.mark_course_completed(course_name)
        return cert

    def certificate_count(self) -> int:
        """Return the number of certificates issued."""
        return len(self._certificates)

    def course_count(self) -> int:
        """Return the number of courses."""
        return len(self._courses)

    def student_certificates(self, student: Student) -> list[Certificate]:
        """Return all certificates belonging to a student."""
        return [c for c in self._certificates if c.student == student]

    def describe(self) -> str:
        return (
            f"CulinarySchool '{self._name}' at {self._address} "
            f"({self.course_count()} courses, "
            f"{self.certificate_count()} certificates)"
        )


class Enrollment:
    """A record of a student enrolled in a course."""

    def __init__(self, student: Student, course: Course, enrolled_on: date) -> None:
        self._student = student
        self._course = course
        self._enrolled_on = enrolled_on
        self._completed = False

    @property
    def student(self) -> Student:
        """Enrolled student."""
        return self._student

    @property
    def course(self) -> Course:
        """Course being taken."""
        return self._course

    def mark_completed(self) -> None:
        """Mark the enrollment as completed."""
        self._completed = True

    def is_completed(self) -> bool:
        """Return True if the enrollment was completed."""
        return self._completed

    def describe(self) -> str:
        status = "completed" if self._completed else "in progress"
        return (
            f"{self._student.full_name()} -> {self._course.name} "
            f"[{status}] since {self._enrolled_on}"
        )


class Workshop:
    """A one-off workshop event."""

    def __init__(self, title: str, day: date, max_participants: int) -> None:
        if max_participants <= 0:
            raise ValueError("Workshop must allow at least one participant")
        self._title = title
        self._day = day
        self._max_participants = max_participants
        self._participants: list[Student] = []

    @property
    def title(self) -> str:
        """Workshop title."""
        return self._title

    def register(self, student: Student) -> None:
        """Register a participant; raise when full."""
        if len(self._participants) >= self._max_participants:
            raise InvalidScheduleError("Workshop is full")
        if student not in self._participants:
            self._participants.append(student)

    def participant_count(self) -> int:
        """Return the number of registered participants."""
        return len(self._participants)

    def is_full(self) -> bool:
        """Return True if the workshop is at capacity."""
        return self.participant_count() >= self._max_participants

    def describe(self) -> str:
        return (
            f"Workshop '{self._title}' on {self._day} "
            f"({self.participant_count()}/{self._max_participants} participants)"
        )
