"""Dishes, portions, courses and menus for the culinary domain."""
from __future__ import annotations

from .allergens import AllergenSet
from .exceptions import InvalidMenuItemError
from .money import Money
from .nutrition import Nutrition
from .recipes import Recipe


class Portion:
    """A serving of a recipe, with optional size scaling."""

    def __init__(self, recipe: Recipe, size_factor: float = 1.0) -> None:
        if size_factor <= 0:
            raise ValueError("Portion size must be positive")
        self._recipe = recipe
        self._size_factor = size_factor

    @property
    def recipe(self) -> Recipe:
        """Recipe used for this portion."""
        return self._recipe

    @property
    def size_factor(self) -> float:
        """Multiplier relative to a standard serving."""
        return self._size_factor

    def cost(self) -> Money:
        """Return the cost of this portion."""
        return self._recipe.cost_per_serving() * self._size_factor

    def nutrition(self) -> Nutrition:
        """Return nutrition for this portion."""
        base = self._recipe.nutrition_per_serving()
        return base.scale(self._size_factor)

    def allergens(self) -> AllergenSet:
        """Return the allergens present in this portion."""
        return self._recipe.allergens()

    def describe(self) -> str:
        """Return a one-line description."""
        return f"{self._size_factor:g}x {self._recipe.name} ({self.cost()})"

    def __str__(self) -> str:
        return self.describe()


class Dish:
    """A plated dish: one portion of a recipe plus garnish and plating notes."""

    def __init__(self, name: str, portion: Portion, plating: str = "") -> None:
        if not name.strip():
            raise ValueError("Dish name must not be empty")
        self._name = name
        self._portion = portion
        self._plating = plating
        self._garnishes: list[str] = []

    @property
    def name(self) -> str:
        """Dish name."""
        return self._name

    @property
    def portion(self) -> Portion:
        """Portion served in this dish."""
        return self._portion

    def add_garnish(self, garnish: str) -> None:
        """Add a garnish to the dish."""
        self._garnishes.append(garnish)

    def remove_garnish(self, garnish: str) -> None:
        """Remove a garnish from the dish."""
        if garnish in self._garnishes:
            self._garnishes.remove(garnish)

    def price_for_sale(self, multiplier: float = 2.5) -> Money:
        """Return the suggested sale price based on cost and multiplier."""
        return self._portion.cost() * multiplier

    def nutrition(self) -> Nutrition:
        """Return nutrition for the dish."""
        return self._portion.nutrition()

    def allergens(self) -> AllergenSet:
        """Return the allergens in the dish."""
        return self._portion.allergens()

    def describe(self) -> str:
        """Return a multi-line description."""
        lines = [f"Dish: {self._name} - {self._portion.describe()}"]
        if self._garnishes:
            lines.append("  Garnish: " + ", ".join(self._garnishes))
        if self._plating:
            lines.append(f"  Plating: {self._plating}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self._name


class Course:
    """One course of a meal (starter, soup, main, dessert, drink)."""

    KINDS = ("starter", "soup", "main", "dessert", "drink")

    def __init__(self, kind: str) -> None:
        if kind not in self.KINDS:
            raise ValueError(f"Unknown course kind: {kind}")
        self._kind = kind
        self._dishes: list[Dish] = []

    @property
    def kind(self) -> str:
        """Course kind."""
        return self._kind

    def add_dish(self, dish: Dish) -> None:
        """Add a dish to the course."""
        self._dishes.append(dish)

    def remove_dish(self, name: str) -> None:
        """Remove a dish by name; raise if it does not exist."""
        for d in self._dishes:
            if d.name == name:
                self._dishes.remove(d)
                return
        raise InvalidMenuItemError(f"Dish {name!r} is not in the course")

    def dish_count(self) -> int:
        """Return the number of dishes in the course."""
        return len(self._dishes)

    def total_cost(self) -> Money:
        """Return the total cost of all dishes."""
        if not self._dishes:
            return Money(0)
        total = self._dishes[0].portion.cost()
        for d in self._dishes[1:]:
            total = total + d.portion.cost()
        return total

    def list_dishes(self) -> list[str]:
        """Return the names of dishes in this course."""
        return [d.name for d in self._dishes]

    def __str__(self) -> str:
        return f"{self._kind}: " + ", ".join(self.list_dishes())


class Menu:
    """A menu made of ordered courses."""

    def __init__(self, title: str) -> None:
        if not title.strip():
            raise ValueError("Menu title must not be empty")
        self._title = title
        self._courses: list[Course] = []

    @property
    def title(self) -> str:
        """Menu title."""
        return self._title

    def add_course(self, course: Course) -> None:
        """Add a course to the menu."""
        self._courses.append(course)

    def remove_course(self, kind: str) -> None:
        """Remove the first course of the given kind."""
        for c in self._courses:
            if c.kind == kind:
                self._courses.remove(c)
                return
        raise InvalidMenuItemError(f"No course of kind {kind!r}")

    def course_count(self) -> int:
        """Return the number of courses."""
        return len(self._courses)

    def dish_count(self) -> int:
        """Return the total number of dishes across all courses."""
        return sum(c.dish_count() for c in self._courses)

    def total_cost(self) -> Money:
        """Return the total cost of the menu."""
        if not self._courses:
            return Money(0)
        total = self._courses[0].total_cost()
        for c in self._courses[1:]:
            total = total + c.total_cost()
        return total

    def allergens(self) -> AllergenSet:
        """Return the union of allergens present in all dishes."""
        result = AllergenSet()
        for course in self._courses:
            for dish in course._dishes:
                result = result.union(dish.allergens())
        return result

    def check_safe_for(self, forbidden: AllergenSet) -> None:
        """Raise AllergenConflictError if the menu contains forbidden allergens."""
        self.allergens().check_compatibility(forbidden)

    def describe(self) -> str:
        """Return a multi-line description of the menu."""
        lines = [f"Menu: {self._title}"]
        for c in self._courses:
            lines.append(f"  {c}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self._title


class MenuPlanner:
    """Builds balanced menus from a pool of recipes."""

    def __init__(self, recipes: list[Recipe]) -> None:
        self._recipes = list(recipes)

    def pick_for_course(self, kind: str, count: int = 1) -> list[Recipe]:
        """Pick ``count`` recipes suitable for the given course."""
        sorted_recipes = sorted(
            self._recipes,
            key=lambda r: r.total_cost().amount_minor,
        )
        if not sorted_recipes:
            return []
        third = max(1, len(sorted_recipes) // 3)
        if kind == "starter":
            pool = sorted_recipes[:third]
        elif kind == "main":
            pool = sorted_recipes[-third:]
        else:
            pool = sorted_recipes
        return pool[:count]

    def build_menu(
        self,
        title: str,
        starters: int,
        mains: int,
        desserts: int,
    ) -> Menu:
        """Assemble a menu using heuristics."""
        menu = Menu(title)
        plan = (
            ("starter", starters),
            ("main", mains),
            ("dessert", desserts),
        )
        for kind, count in plan:
            course = Course(kind)
            for recipe in self.pick_for_course(kind, count):
                portion = Portion(recipe)
                dish = Dish(f"{kind}: {recipe.name}", portion)
                course.add_dish(dish)
            menu.add_course(course)
        return menu

    def count_recipes(self) -> int:
        """Return how many recipes the planner knows about."""
        return len(self._recipes)

    def cheapest(self) -> Recipe:
        """Return the cheapest recipe; raise if the pool is empty."""
        if not self._recipes:
            raise InvalidMenuItemError("No recipes available")
        return min(self._recipes, key=lambda r: r.total_cost().amount_minor)
