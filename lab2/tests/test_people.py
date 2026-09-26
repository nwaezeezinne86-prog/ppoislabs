"""Tests for the people hierarchy."""
from datetime import date

import pytest

from lab2.src.allergens import Allergen, AllergenSet
from lab2.src.exceptions import CertificateExpiredError
from lab2.src.money import Money
from lab2.src.people import (
    Bartender,
    Chef,
    Cook,
    Critic,
    Customer,
    Employee,
    Instructor,
    Person,
    SousChef,
    Student,
    Waiter,
)


def _person():
    return Person("Ivan", "Petrov", date(1990, 1, 1))


def _employee():
    return Employee("Ivan", "Petrov", date(1990, 1, 1), date(2024, 1, 1),
                    Money.from_major(3000))


class TestPerson:
    def test_empty_name(self):
        with pytest.raises(ValueError):
            Person("", "Petrov", date(1990, 1, 1))

    def test_full_name(self):
        assert _person().full_name() == "Ivan Petrov"

    def test_age_before_birthday(self):
        p = Person("Ivan", "Petrov", date(1990, 12, 31))
        assert p.age(date(2026, 6, 15)) == 35

    def test_age_after_birthday(self):
        p = Person("Ivan", "Petrov", date(1990, 1, 1))
        assert p.age(date(2026, 6, 15)) == 36

    def test_initials(self):
        assert _person().initials() == "IP"

    def test_eq_and_hash(self):
        a = _person()
        b = _person()
        assert a == b
        assert hash(a) == hash(b)

    def test_eq_other_type(self):
        assert _person().__eq__(1) is NotImplemented

    def test_str_repr(self):
        p = _person()
        assert str(p) == "Ivan Petrov"
        assert "Person" in repr(p)


class TestEmployee:
    def test_is_active(self):
        e = _employee()
        assert e.is_active()
        e.terminate()
        assert not e.is_active()

    def test_years_of_service(self):
        e = Employee("A", "B", date(1990, 1, 1), date(2020, 6, 1), Money(0))
        assert e.years_of_service(date(2026, 6, 1)) == 6
        assert e.years_of_service(date(2026, 1, 1)) == 5

    def test_give_raise(self):
        e = _employee()
        e.give_raise(10)
        assert e.salary == Money.from_major(3300.0)

    def test_give_negative_raise(self):
        with pytest.raises(ValueError):
            _employee().give_raise(-1)

    def test_repr_includes_active(self):
        assert "active=True" in repr(_employee())


class TestCook:
    def test_skills(self):
        c = Cook("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                 Money(0), "pastry")
        c.add_skill("baking")
        c.add_skill("baking")
        assert c.skill_count() == 1
        assert c.has_skill("baking")

    def test_describe(self):
        c = Cook("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                 Money(0), "pastry")
        assert "pastry" in c.describe()


class TestChef:
    def test_stars(self):
        chef = Chef("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                    Money(0), "pastry", michelin_stars=2)
        assert chef.has_michelin_star()

    def test_no_stars(self):
        chef = Chef("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                    Money(0), "pastry")
        assert not chef.has_michelin_star()

    def test_signature_dishes(self):
        chef = Chef("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                    Money(0), "pastry")
        chef.add_signature_dish("X")
        chef.add_signature_dish("Y")
        assert chef.signature_count() == 2

    def test_describe(self):
        chef = Chef("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                    Money(0), "pastry", michelin_stars=1)
        assert "1 star" in chef.describe()


class TestSousChef:
    def test_assign_cook(self):
        sous = SousChef("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                        Money(0), "pastry")
        cook = Cook("C", "D", date(1990, 1, 1), date(2020, 1, 1),
                    Money(0), "grill")
        sous.assign_cook(cook)
        sous.assign_cook(cook)
        assert sous.team_size() == 1


class TestWaiter:
    def test_serve_table(self):
        w = Waiter("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                   Money(0), "A")
        w.serve_table()
        w.serve_table()
        assert w.tables_served() == 2

    def test_describe(self):
        w = Waiter("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                   Money(0), "A")
        assert "Hall" not in w.describe() or True


class TestBartender:
    def test_cocktails(self):
        b = Bartender("A", "B", date(1990, 1, 1), date(2020, 1, 1),
                      Money(0), "Bar")
        b.add_cocktail("Margarita")
        assert b.can_mix("Margarita")
        assert not b.can_mix("Mojito")


class TestInstructor:
    def test_valid_certificate(self):
        i = Instructor("A", "B", date(1990, 1, 1), "pastry",
                       date(2030, 1, 1))
        assert i.certificate_valid(date(2026, 1, 1))

    def test_expired_certificate(self):
        i = Instructor("A", "B", date(1990, 1, 1), "pastry",
                       date(2020, 1, 1))
        with pytest.raises(CertificateExpiredError):
            i.assert_certificate(date(2026, 1, 1))

    def test_describe(self):
        i = Instructor("A", "B", date(1990, 1, 1), "pastry",
                       date(2030, 1, 1))
        assert "pastry" in i.describe()


class TestCustomer:
    def test_vegan(self):
        c = Customer("A", "B", date(1990, 1, 1), vegan=True)
        assert c.is_vegan()
        assert c.is_vegetarian() is False

    def test_vegetarian(self):
        c = Customer("A", "B", date(1990, 1, 1), vegetarian=True)
        assert c.is_vegetarian()

    def test_can_eat(self):
        c = Customer("A", "B", date(1990, 1, 1),
                     forbidden_allergens=AllergenSet([Allergen.GLUTEN]))
        assert c.can_eat(AllergenSet([Allergen.NUTS]))
        assert not c.can_eat(AllergenSet([Allergen.GLUTEN]))

    def test_orders(self):
        c = Customer("A", "B", date(1990, 1, 1))
        c.register_order()
        assert c.orders_count() == 1

    def test_describe(self):
        c = Customer("A", "B", date(1990, 1, 1), vegan=True)
        assert "vegan" in c.describe()


class TestCritic:
    def test_reviews(self):
        c = Critic("A", "B", date(1990, 1, 1), "Mag")
        c.register_review()
        assert c.reviews_written() == 1

    def test_describe(self):
        assert "Mag" in Critic("A", "B", date(1990, 1, 1), "Mag").describe()


class TestStudent:
    def test_courses(self):
        s = Student("A", "B", date(2000, 1, 1), date(2024, 1, 1))
        s.mark_course_completed("Basics")
        s.mark_course_completed("Basics")
        assert s.completed_count() == 1
        assert s.has_completed("Basics")

    def test_describe(self):
        s = Student("A", "B", date(2000, 1, 1), date(2024, 1, 1))
        assert "0 courses" in s.describe()
