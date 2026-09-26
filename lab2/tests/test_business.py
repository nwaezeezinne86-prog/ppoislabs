"""Tests for restaurants, branches, tables, reservations, reviews."""
from datetime import date, time

import pytest

from lab2.src.business import (
    Branch,
    Promotion,
    Reservation,
    Restaurant,
    Review,
    Table,
)
from lab2.src.exceptions import (
    ReservationConflictError,
    TableNotFoundError,
)


def _branch():
    b = Branch("Center", "Minsk", 50)
    b.add_table(Table(1, 4))
    b.add_table(Table(2, 2, "terrace"))
    return b


class TestTable:
    def test_bad_number(self):
        with pytest.raises(ValueError):
            Table(0, 4)

    def test_bad_seats(self):
        with pytest.raises(ValueError):
            Table(1, 0)

    def test_can_host(self):
        t = Table(1, 4)
        assert t.can_host(4)
        assert not t.can_host(5)
        assert not t.can_host(0)

    def test_describe(self):
        assert "Table" in Table(1, 4).describe()


class TestReservation:
    def test_bad_hours(self):
        t = Table(1, 4)
        with pytest.raises(ValueError):
            Reservation("A", t, date(2026, 9, 28), time(18, 0), 0)

    def test_overlaps_same_day(self):
        t = Table(1, 4)
        a = Reservation("A", t, date(2026, 9, 28), time(18, 0), 2)
        b = Reservation("B", t, date(2026, 9, 28), time(19, 0), 2)
        assert a.overlaps(b)

    def test_no_overlap_different_day(self):
        t = Table(1, 4)
        a = Reservation("A", t, date(2026, 9, 28), time(18, 0), 2)
        b = Reservation("B", t, date(2026, 9, 29), time(18, 0), 2)
        assert not a.overlaps(b)

    def test_no_overlap_same_time(self):
        t = Table(1, 4)
        a = Reservation("A", t, date(2026, 9, 28), time(18, 0), 2)
        b = Reservation("B", t, date(2026, 9, 28), time(20, 0), 2)
        assert not a.overlaps(b)

    def test_cancel(self):
        r = Reservation("A", Table(1, 4), date(2026, 9, 28), time(18, 0), 2)
        r.cancel()
        assert r.is_cancelled()

    def test_describe(self):
        r = Reservation("A", Table(1, 4), date(2026, 9, 28), time(18, 0), 2)
        assert "A" in r.describe()


class TestReview:
    def test_bad_rating(self):
        with pytest.raises(ValueError):
            Review("A", 0, "x")
        with pytest.raises(ValueError):
            Review("A", 6, "x")

    def test_is_positive(self):
        assert Review("A", 5, "x").is_positive()
        assert not Review("A", 3, "x").is_positive()

    def test_vote_helpful(self):
        r = Review("A", 5, "x")
        r.vote_helpful()
        r.vote_helpful()
        assert r.helpful_votes() == 2

    def test_describe(self):
        assert "A" in Review("A", 5, "x").describe()


class TestPromotion:
    def test_bad_discount(self):
        with pytest.raises(ValueError):
            Promotion("X", 0)
        with pytest.raises(ValueError):
            Promotion("X", 101)

    def test_deactivate(self):
        p = Promotion("X", 10)
        p.deactivate()
        assert not p.is_active()

    def test_apply(self):
        p = Promotion("X", 20)
        assert p.apply_to(1000) == 800

    def test_describe(self):
        assert "X" in Promotion("X", 10).describe()


class TestBranch:
    def test_add_table_and_find(self):
        b = _branch()
        assert b.table_count() == 2
        assert b.find_table(2).seats == 2

    def test_find_missing(self):
        with pytest.raises(TableNotFoundError):
            _branch().find_table(99)

    def test_reserve(self):
        b = _branch()
        r = b.reserve("Ivan", 1, date(2026, 9, 28), time(18, 0), 2)
        assert r.customer_name == "Ivan"
        assert b.reservation_count() == 1

    def test_reserve_conflict(self):
        b = _branch()
        b.reserve("Ivan", 1, date(2026, 9, 28), time(18, 0), 2)
        with pytest.raises(ReservationConflictError):
            b.reserve("Petrov", 1, date(2026, 9, 28), time(19, 0), 2)

    def test_reserve_skips_cancelled(self):
        b = _branch()
        r1 = b.reserve("Ivan", 1, date(2026, 9, 28), time(18, 0), 2)
        r1.cancel()
        b.reserve("Petrov", 1, date(2026, 9, 28), time(19, 0), 2)   # no raise

    def test_average_rating(self):
        b = _branch()
        assert b.average_rating() == 0.0
        b.add_review(Review("A", 5, ""))
        b.add_review(Review("B", 3, ""))
        assert b.average_rating() == 4.0

    def test_describe(self):
        assert "Center" in _branch().describe()


class TestRestaurant:
    def test_empty_name(self):
        with pytest.raises(ValueError):
            Restaurant("")

    def test_add_find_remove_branch(self):
        r = Restaurant("Tasty")
        b = _branch()
        r.add_branch(b)
        assert r.find_branch("Center") is b
        r.remove_branch("Center")
        assert r.find_branch("Center") is None

    def test_promotions(self):
        r = Restaurant("Tasty")
        p = Promotion("Happy", 10)
        r.add_promotion(p)
        assert len(r.active_promotions()) == 1
        p.deactivate()
        assert len(r.active_promotions()) == 0

    def test_overall_rating_no_reviews(self):
        r = Restaurant("Tasty")
        r.add_branch(_branch())
        assert r.overall_rating() == 0.0

    def test_overall_rating_with_reviews(self):
        r = Restaurant("Tasty")
        b = _branch()
        b.add_review(Review("A", 5, ""))
        r.add_branch(b)
        assert r.overall_rating() == 5.0

    def test_describe(self):
        r = Restaurant("Tasty")
        r.add_branch(_branch())
        assert "Tasty" in r.describe()
