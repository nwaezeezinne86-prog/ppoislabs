"""People in the culinary domain: chefs, cooks, waiters, customers, critics."""
from __future__ import annotations

from datetime import date

from .allergens import AllergenSet
from .exceptions import CertificateExpiredError
from .money import Money


class Person:
    """Base class for everyone in the domain."""

    def __init__(self, first_name: str, last_name: str, birth_date: date) -> None:
        if not first_name.strip() or not last_name.strip():
            raise ValueError("First and last name must not be empty")
        self._first_name = first_name
        self._last_name = last_name
        self._birth_date = birth_date

    @property
    def first_name(self) -> str:
        """First name."""
        return self._first_name

    @property
    def last_name(self) -> str:
        """Last name."""
        return self._last_name

    @property
    def birth_date(self) -> date:
        """Date of birth."""
        return self._birth_date

    def full_name(self) -> str:
        """Return 'First Last'."""
        return f"{self._first_name} {self._last_name}"

    def age(self, today: date) -> int:
        """Return the age in full years."""
        years = today.year - self._birth_date.year
        if (today.month, today.day) < (self._birth_date.month, self._birth_date.day):
            years -= 1
        return years

    def initials(self) -> str:
        """Return initials, e.g. 'AB'."""
        return (self._first_name[:1] + self._last_name[:1]).upper()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Person):
            return NotImplemented
        return (
            self.full_name() == other.full_name()
            and self._birth_date == other._birth_date
        )

    def __hash__(self) -> int:
        return hash((self.full_name(), self._birth_date))

    def __str__(self) -> str:
        return self.full_name()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._first_name!r}, {self._last_name!r})"


class Employee(Person):
    """A person who works for the restaurant."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        hire_date: date,
        salary: Money,
    ) -> None:
        super().__init__(first_name, last_name, birth_date)
        self._hire_date = hire_date
        self._salary = salary
        self._active = True

    @property
    def salary(self) -> Money:
        """Monthly salary."""
        return self._salary

    @property
    def hire_date(self) -> date:
        """Date the employee was hired."""
        return self._hire_date

    def is_active(self) -> bool:
        """Return True while the employee works here."""
        return self._active

    def terminate(self) -> None:
        """Mark the employee as inactive."""
        self._active = False

    def years_of_service(self, today: date) -> int:
        """Return full years of service."""
        years = today.year - self._hire_date.year
        if (today.month, today.day) < (self._hire_date.month, self._hire_date.day):
            years -= 1
        return years

    def give_raise(self, percent: float) -> None:
        """Increase the salary by ``percent`` %."""
        if percent < 0:
            raise ValueError("Raise percent must be non-negative")
        self._salary = self._salary * (1 + percent / 100.0)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self._first_name!r}, "
            f"{self._last_name!r}, active={self._active})"
        )


class Cook(Employee):
    """A cook with a set of skills."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        hire_date: date,
        salary: Money,
        specialty: str,
    ) -> None:
        super().__init__(first_name, last_name, birth_date, hire_date, salary)
        self._specialty = specialty
        self._skills: set[str] = set()

    def add_skill(self, skill: str) -> None:
        """Register a new skill."""
        self._skills.add(skill)

    def has_skill(self, skill: str) -> bool:
        """Return True if the cook has the given skill."""
        return skill in self._skills

    def skill_count(self) -> int:
        """Return the number of skills."""
        return len(self._skills)

    def describe(self) -> str:
        """Return a one-line description."""
        return (
            f"Cook {self.full_name()} ({self._specialty}), "
            f"{self.skill_count()} skills"
        )


class Chef(Cook):
    """A chef who can run a kitchen."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        hire_date: date,
        salary: Money,
        specialty: str,
        michelin_stars: int = 0,
    ) -> None:
        super().__init__(
            first_name, last_name, birth_date, hire_date, salary, specialty
        )
        self._michelin_stars = max(0, michelin_stars)
        self._signature_dishes: list[str] = []

    def add_signature_dish(self, name: str) -> None:
        """Add a signature dish name."""
        self._signature_dishes.append(name)

    def has_michelin_star(self) -> bool:
        """Return True if the chef has at least one Michelin star."""
        return self._michelin_stars > 0

    def signature_count(self) -> int:
        """Return the number of signature dishes."""
        return len(self._signature_dishes)

    def describe(self) -> str:
        """Return a one-line description."""
        stars = f", {self._michelin_stars} star(s)" if self._michelin_stars else ""
        return f"Chef {self.full_name()} ({self._specialty}){stars}"


class SousChef(Chef):
    """Second-in-command in the kitchen."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        hire_date: date,
        salary: Money,
        specialty: str,
        michelin_stars: int = 0,
    ) -> None:
        super().__init__(
            first_name, last_name, birth_date, hire_date, salary, specialty,
            michelin_stars,
        )
        self._manages: list[Cook] = []

    def assign_cook(self, cook: Cook) -> None:
        """Put a cook under this sous-chef."""
        if cook not in self._manages:
            self._manages.append(cook)

    def team_size(self) -> int:
        """Return the number of cooks managed."""
        return len(self._manages)


class Waiter(Employee):
    """A waiter serving customers."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        hire_date: date,
        salary: Money,
        section: str,
    ) -> None:
        super().__init__(first_name, last_name, birth_date, hire_date, salary)
        self._section = section
        self._tables_served = 0

    def serve_table(self) -> None:
        """Increment the counter of served tables."""
        self._tables_served += 1

    def tables_served(self) -> int:
        """Return the total number of served tables."""
        return self._tables_served

    def describe(self) -> str:
        return (
            f"Waiter {self.full_name()} (section {self._section}, "
            f"{self._tables_served} tables)"
        )


class Bartender(Employee):
    """A bartender with a list of cocktails on the menu."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        hire_date: date,
        salary: Money,
        bar_name: str,
    ) -> None:
        super().__init__(first_name, last_name, birth_date, hire_date, salary)
        self._bar_name = bar_name
        self._cocktails: set[str] = set()

    def add_cocktail(self, name: str) -> None:
        """Register a cocktail the bartender can mix."""
        self._cocktails.add(name)

    def can_mix(self, name: str) -> bool:
        """Return True if the bartender can mix the cocktail."""
        return name in self._cocktails

    def describe(self) -> str:
        return (
            f"Bartender {self.full_name()} at {self._bar_name} "
            f"({len(self._cocktails)} cocktails)"
        )


class Instructor(Person):
    """An instructor who teaches culinary classes."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        specialization: str,
        certificate_expiry: date,
    ) -> None:
        super().__init__(first_name, last_name, birth_date)
        self._specialization = specialization
        self._certificate_expiry = certificate_expiry

    def certificate_valid(self, today: date) -> bool:
        """Return True if the certificate is still valid."""
        return today <= self._certificate_expiry

    def assert_certificate(self, today: date) -> None:
        """Raise CertificateExpiredError if the certificate has expired."""
        if not self.certificate_valid(today):
            raise CertificateExpiredError(
                f"Instructor {self.full_name()} certificate expired"
            )

    def describe(self) -> str:
        return f"Instructor {self.full_name()} ({self._specialization})"


class Customer(Person):
    """A restaurant customer with dietary preferences."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        forbidden_allergens: AllergenSet | None = None,
        vegetarian: bool = False,
        vegan: bool = False,
    ) -> None:
        super().__init__(first_name, last_name, birth_date)
        self._forbidden = forbidden_allergens or AllergenSet()
        self._vegetarian = vegetarian
        self._vegan = vegan
        self._orders_count = 0

    @property
    def forbidden_allergens(self) -> AllergenSet:
        """Allergens the customer cannot eat."""
        return self._forbidden

    def is_vegetarian(self) -> bool:
        """Return True for vegetarian customers."""
        return self._vegetarian

    def is_vegan(self) -> bool:
        """Return True for vegan customers."""
        return self._vegan

    def register_order(self) -> None:
        """Record that the customer has placed one more order."""
        self._orders_count += 1

    def orders_count(self) -> int:
        """Return the total number of orders placed."""
        return self._orders_count

    def can_eat(self, allergens: AllergenSet) -> bool:
        """Return True if the given allergen set is compatible with the customer."""
        return not allergens.intersects(self._forbidden)

    def describe(self) -> str:
        diet = "vegan" if self._vegan else (
            "vegetarian" if self._vegetarian else "regular"
        )
        return f"Customer {self.full_name()} ({diet})"


class Critic(Person):
    """A restaurant critic who writes reviews."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        publication: str,
    ) -> None:
        super().__init__(first_name, last_name, birth_date)
        self._publication = publication
        self._reviews_written = 0

    def register_review(self) -> None:
        """Record that the critic wrote a review."""
        self._reviews_written += 1

    def reviews_written(self) -> int:
        """Return the number of reviews written."""
        return self._reviews_written

    def describe(self) -> str:
        return f"Critic {self.full_name()} from {self._publication}"


class Student(Person):
    """A student of a culinary school."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        birth_date: date,
        enrollment_date: date,
    ) -> None:
        super().__init__(first_name, last_name, birth_date)
        self._enrollment_date = enrollment_date
        self._completed_courses: set[str] = set()

    def mark_course_completed(self, course_name: str) -> None:
        """Mark a course as completed."""
        self._completed_courses.add(course_name)

    def completed_count(self) -> int:
        """Return how many courses the student completed."""
        return len(self._completed_courses)

    def has_completed(self, course_name: str) -> bool:
        """Return True if the student completed the given course."""
        return course_name in self._completed_courses

    def describe(self) -> str:
        return f"Student {self.full_name()} ({self.completed_count()} courses)"
