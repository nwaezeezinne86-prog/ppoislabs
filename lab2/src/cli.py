"""Console UI for the culinary domain. Fully decoupled from the domain layer."""
from __future__ import annotations

import sys
from datetime import date, time

from .allergens import Allergen, AllergenSet
from .business import Branch, Promotion, Restaurant, Review, Table
from .dishes import Course, Dish, Menu, MenuPlanner, Portion
from .education import Course as EduCourse, CulinarySchool, Lesson, Workshop
from .exceptions import CulinaryException
from .ingredients import Fish, Meat, Spice, Vegetable
from .money import Money
from .people import Chef, Cook, Customer, Instructor, Student, Waiter
from .recipes import Recipe, RecipeBook, RecipeIngredient, RecipeStep
from .technique import Bake, Boil, Fry, Grill, Mix, Steam
from .units import Quantity, Unit


def _read(prompt: str) -> str:
    return input(prompt).strip()


def _menu(title: str, items: list[str]) -> None:
    print(f"\n=== {title} ===")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    print("  0. Back")


# ----------------------------------------------------------------------
# Recipes submenu
# ----------------------------------------------------------------------
def recipes_menu(book: RecipeBook) -> None:
    """Manage a recipe book."""
    while True:
        print(f"\n{book}")
        _menu("Recipes", [
            "Add recipe",
            "Show recipe",
            "List all recipes",
            "Delete recipe",
            "Search by max cost",
        ])
        choice = _read("Choice: ")
        try:
            if choice == "1":
                _add_recipe(book)
            elif choice == "2":
                name = _read("Recipe name: ")
                print(book.find(name).describe())
            elif choice == "3":
                for r in book.all():
                    print(" -", r)
            elif choice == "4":
                name = _read("Recipe name: ")
                book.remove(name)
                print("Removed")
            elif choice == "5":
                limit = Money.from_major(float(_read("Max RUB: ")))
                for r in book.find_cheaper_than(limit):
                    print(" -", r)
            elif choice == "0":
                return
        except (CulinaryException, ValueError) as exc:
            print(f"Error: {exc}")


def _add_recipe(book: RecipeBook) -> None:
    name = _read("Recipe name: ")
    servings = int(_read("Servings: "))
    recipe = Recipe(name, servings)
    while True:
        ingredient_name = _read("Ingredient (or empty): ")
        if not ingredient_name:
            break
        unit = Unit(_read("Unit (g/kg/ml/l/pc/tsp/tbsp/cup): "))
        amount = float(_read("Amount: "))
        price = Money.from_major(float(_read("Price per unit RUB: ")))
        ing = Vegetable(ingredient_name, unit, price, 1, 12)
        recipe.add_ingredient(RecipeIngredient(ing, Quantity(amount, unit)))
    step_num = 1
    while True:
        descr = _read("Step description (or empty): ")
        if not descr:
            break
        minutes = int(_read("Minutes: "))
        technique = Boil()
        recipe.add_step(RecipeStep(step_num, descr, technique, minutes))
        step_num += 1
    book.add(recipe)
    print(f"Added {recipe}")


# ----------------------------------------------------------------------
# Menu submenu
# ----------------------------------------------------------------------
def menu_menu(book: RecipeBook, menus: list[Menu]) -> None:
    """Compose restaurant menus from recipes."""
    while True:
        _menu("Menus", [
            "Build menu from recipes",
            "Show menu",
            "List all menus",
        ])
        choice = _read("Choice: ")
        try:
            if choice == "1":
                title = _read("Menu title: ")
                starters = int(_read("Starters: "))
                mains = int(_read("Mains: "))
                desserts = int(_read("Desserts: "))
                planner = MenuPlanner(book.all())
                menu = planner.build_menu(title, starters, mains, desserts)
                menus.append(menu)
                print(menu.describe())
            elif choice == "2":
                title = _read("Menu title: ")
                for m in menus:
                    if m.title == title:
                        print(m.describe())
                        break
            elif choice == "3":
                for m in menus:
                    print(" -", m.describe())
            elif choice == "0":
                return
        except (CulinaryException, ValueError) as exc:
            print(f"Error: {exc}")


# ----------------------------------------------------------------------
# People submenu
# ----------------------------------------------------------------------
def people_menu(staff: list, customers: list) -> None:
    """Register employees and customers."""
    while True:
        _menu("People", [
            "Hire chef",
            "Hire waiter",
            "Register customer",
            "List staff",
        ])
        choice = _read("Choice: ")
        try:
            if choice == "1":
                first = _read("First name: ")
                last = _read("Last name: ")
                birth = date.fromisoformat(_read("Birth YYYY-MM-DD: "))
                hire = date.fromisoformat(_read("Hire YYYY-MM-DD: "))
                salary = Money.from_major(float(_read("Salary RUB: ")))
                specialty = _read("Specialty: ")
                stars = int(_read("Michelin stars: "))
                chef = Chef(first, last, birth, hire, salary, specialty, stars)
                staff.append(chef)
                print(chef.describe())
            elif choice == "2":
                first = _read("First name: ")
                last = _read("Last name: ")
                birth = date.fromisoformat(_read("Birth YYYY-MM-DD: "))
                hire = date.fromisoformat(_read("Hire YYYY-MM-DD: "))
                salary = Money.from_major(float(_read("Salary RUB: ")))
                section = _read("Section: ")
                waiter = Waiter(first, last, birth, hire, salary, section)
                staff.append(waiter)
                print(waiter.describe())
            elif choice == "3":
                first = _read("First name: ")
                last = _read("Last name: ")
                birth = date.fromisoformat(_read("Birth YYYY-MM-DD: "))
                veget = _read("Vegetarian? (y/n): ").lower() == "y"
                customer = Customer(first, last, birth, vegetarian=veget)
                customers.append(customer)
                print(customer.describe())
            elif choice == "4":
                for p in staff:
                    print(" -", p.full_name())
            elif choice == "0":
                return
        except (CulinaryException, ValueError) as exc:
            print(f"Error: {exc}")


# ----------------------------------------------------------------------
# Business submenu
# ----------------------------------------------------------------------
def business_menu(restaurants: list[Restaurant]) -> None:
    """Restaurant operations."""
    while True:
        _menu("Restaurant", [
            "Add restaurant",
            "Add branch",
            "Add table",
            "Reserve table",
            "Add review",
            "Show restaurant info",
        ])
        choice = _read("Choice: ")
        try:
            if choice == "1":
                name = _read("Restaurant name: ")
                restaurants.append(Restaurant(name))
                print("Added")
            elif choice == "2":
                rest = _pick(restaurants, "Restaurant name: ")
                if rest is None:
                    continue
                branch = Branch(
                    _read("Branch name: "),
                    _read("Address: "),
                    int(_read("Seats: ")),
                )
                rest.add_branch(branch)
                print(branch.describe())
            elif choice == "3":
                rest = _pick(restaurants, "Restaurant name: ")
                if rest is None:
                    continue
                branch_name = _read("Branch name: ")
                branch = rest.find_branch(branch_name)
                if branch is None:
                    print("Branch not found")
                    continue
                table = Table(
                    int(_read("Table number: ")),
                    int(_read("Seats: ")),
                    _read("Location: "),
                )
                branch.add_table(table)
                print(table.describe())
            elif choice == "4":
                rest = _pick(restaurants, "Restaurant name: ")
                if rest is None:
                    continue
                branch = rest.find_branch(_read("Branch name: "))
                if branch is None:
                    print("Branch not found")
                    continue
                res = branch.reserve(
                    _read("Customer: "),
                    int(_read("Table number: ")),
                    date.fromisoformat(_read("Date YYYY-MM-DD: ")),
                    time.fromisoformat(_read("Start HH:MM: ")),
                    int(_read("Hours: ")),
                )
                print(res.describe())
            elif choice == "5":
                rest = _pick(restaurants, "Restaurant name: ")
                if rest is None:
                    continue
                branch = rest.find_branch(_read("Branch name: "))
                if branch is None:
                    print("Branch not found")
                    continue
                review = Review(
                    _read("Author: "),
                    int(_read("Rating 1-5: ")),
                    _read("Text: "),
                )
                branch.add_review(review)
                print("Average rating:", branch.average_rating())
            elif choice == "6":
                rest = _pick(restaurants, "Restaurant name: ")
                if rest is None:
                    continue
                print(rest.describe())
            elif choice == "0":
                return
        except (CulinaryException, ValueError) as exc:
            print(f"Error: {exc}")


def _pick(items: list, prompt: str):
    name = _read(prompt)
    for item in items:
        if getattr(item, "name", None) == name:
            return item
    print("Not found")
    return None


# ----------------------------------------------------------------------
# Education submenu
# ----------------------------------------------------------------------
def education_menu(schools: list[CulinarySchool]) -> None:
    """Manage culinary schools."""
    while True:
        _menu("Education", [
            "Add school",
            "Add course",
            "Enroll student",
            "Award certificate",
            "Show school info",
        ])
        choice = _read("Choice: ")
        try:
            if choice == "1":
                name = _read("School name: ")
                schools.append(CulinarySchool(name, _read("Address: ")))
                print("Added")
            elif choice == "2":
                school = _pick(schools, "School name: ")
                if school is None:
                    continue
                course = EduCourse(
                    _read("Course name: "),
                    Money.from_major(float(_read("Price RUB: "))),
                    int(_read("Capacity: ")),
                )
                school.add_course(course)
                print(course.describe())
            elif choice == "3":
                school = _pick(schools, "School name: ")
                if school is None:
                    continue
                course = school.find_course(_read("Course name: "))
                if course is None:
                    print("Course not found")
                    continue
                student = Student(
                    _read("First name: "),
                    _read("Last name: "),
                    date.fromisoformat(_read("Birth YYYY-MM-DD: ")),
                    date.today(),
                )
                course.enroll(student)
                print(course.describe())
            elif choice == "4":
                school = _pick(schools, "School name: ")
                if school is None:
                    continue
                course_name = _read("Course name: ")
                student = Student(
                    _read("First name: "),
                    _read("Last name: "),
                    date.fromisoformat(_read("Birth YYYY-MM-DD: ")),
                    date.today(),
                )
                cert = school.award_certificate(student, course_name, date.today())
                print(cert.describe())
            elif choice == "5":
                school = _pick(schools, "School name: ")
                if school is not None:
                    print(school.describe())
            elif choice == "0":
                return
        except (CulinaryException, ValueError) as exc:
            print(f"Error: {exc}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main() -> int:
    """CLI entry point."""
    book = RecipeBook("My Cookbook")
    menus: list[Menu] = []
    staff: list = []
    customers: list = []
    restaurants: list[Restaurant] = []
    schools: list[CulinarySchool] = []

    while True:
        _menu("Culinary main menu", [
            "Recipes",
            "Menus",
            "People",
            "Restaurant",
            "Education",
        ])
        choice = _read("Choice: ")
        if choice == "1":
            recipes_menu(book)
        elif choice == "2":
            menu_menu(book, menus)
        elif choice == "3":
            people_menu(staff, customers)
        elif choice == "4":
            business_menu(restaurants)
        elif choice == "5":
            education_menu(schools)
        elif choice == "0":
            print("Goodbye!")
            return 0


if __name__ == "__main__":
    sys.exit(main())
