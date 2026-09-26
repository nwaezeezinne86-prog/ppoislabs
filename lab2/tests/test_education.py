"""Tests for culinary education."""
from datetime import date

import pytest

from lab2.src.education import (
    Certificate,
    Course,
    CulinarySchool,
    Enrollment,
    Lesson,
    Workshop,
)
from lab2.src.exceptions import CertificateExpiredError, InvalidScheduleError
from lab2.src.money import Money
from lab2.src.people import Instructor, Student


def _instructor():
    return Instructor("Maria", "K", date(1975, 5, 5), "Pastry", date(2030, 1, 1))


def _student(name: str = "Ivan"):
    return Student(name, "Petrov", date(2000, 1, 1), date(2024, 9, 1))


def _course(name: str = "Basics", capacity: int = 2) -> Course:
    c = Course(name, Money.from_major(500), capacity)
    c.add_lesson(Lesson("Knife skills", date(2026, 10, 1), 90, _instructor()))
    c.add_lesson(Lesson("Sauces", date(2026, 10, 8), 120, _instructor()))
    return c


class TestLesson:
    def test_bad_duration(self):
        with pytest.raises(ValueError):
            Lesson("X", date(2026, 10, 1), 0, _instructor())

    def test_attendance(self):
        lesson = Lesson("X", date(2026, 10, 1), 30, _instructor())
        s1 = _student()
        s2 = _student("Anna")
        lesson.mark_attended(s1)
        lesson.mark_attended(s1)   # duplicate
        lesson.mark_attended(s2)
        assert lesson.attendance_count() == 2

    def test_describe(self):
        assert "Knife" in Lesson("Knife", date(2026, 10, 1), 30, _instructor()).describe()


class TestCourse:
    def test_bad_name(self):
        with pytest.raises(ValueError):
            Course("  ", Money(0))

    def test_bad_capacity(self):
        with pytest.raises(ValueError):
            Course("X", Money(0), capacity=0)

    def test_enroll_and_full(self):
        c = _course(capacity=1)
        c.enroll(_student())
        assert c.is_full()
        with pytest.raises(InvalidScheduleError):
            c.enroll(_student("B"))

    def test_enroll_duplicate_ok(self):
        c = _course()
        s = _student()
        c.enroll(s)
        c.enroll(s)
        assert c.enrolled_count() == 1

    def test_total_minutes(self):
        assert _course().total_minutes() == 210

    def test_describe(self):
        assert "Basics" in _course().describe()


class TestCulinarySchool:
    def test_add_find_course(self):
        school = CulinarySchool("Academy", "Minsk")
        c = _course()
        school.add_course(c)
        assert school.find_course("Basics") is c
        assert school.find_course("Missing") is None

    def test_award_certificate_requires_enrollment(self):
        school = CulinarySchool("Academy", "Minsk")
        school.add_course(_course())
        with pytest.raises(CertificateExpiredError):
            school.award_certificate(_student(), "Basics", date(2026, 12, 1))

    def test_award_certificate(self):
        school = CulinarySchool("Academy", "Minsk")
        c = _course()
        school.add_course(c)
        s = _student()
        c.enroll(s)
        cert = school.award_certificate(s, "Basics", date(2026, 12, 1))
        assert cert.course_name == "Basics"
        assert school.certificate_count() == 1
        assert s.has_completed("Basics")

    def test_student_certificates(self):
        school = CulinarySchool("Academy", "Minsk")
        c = _course()
        school.add_course(c)
        s = _student()
        c.enroll(s)
        school.award_certificate(s, "Basics", date(2026, 12, 1))
        assert len(school.student_certificates(s)) == 1

    def test_describe(self):
        school = CulinarySchool("Academy", "Minsk")
        assert "Academy" in school.describe()


class TestEnrollment:
    def test_mark_completed(self):
        e = Enrollment(_student(), _course(), date(2026, 9, 1))
        e.mark_completed()
        assert e.is_completed()

    def test_describe(self):
        e = Enrollment(_student(), _course(), date(2026, 9, 1))
        assert "Ivan" in e.describe()


class TestWorkshop:
    def test_bad_capacity(self):
        with pytest.raises(ValueError):
            Workshop("X", date(2026, 1, 1), 0)

    def test_register_and_full(self):
        w = Workshop("Sushi", date(2026, 11, 1), max_participants=1)
        w.register(_student())
        assert w.is_full()
        with pytest.raises(InvalidScheduleError):
            w.register(_student("B"))

    def test_describe(self):
        assert "Sushi" in Workshop("Sushi", date(2026, 11, 1), 2).describe()


class TestCertificate:
    def test_age_days(self):
        c = Certificate(_student(), "X", date(2026, 1, 1))
        assert c.age_days(date(2026, 1, 11)) == 10

    def test_describe(self):
        c = Certificate(_student(), "X", date(2026, 1, 1))
        assert "Ivan" in c.describe()
