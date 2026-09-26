"""Recipes and recipe book for the culinary domain."""
from __future__ import annotations

from .allergens import AllergenSet
from .exceptions import IngredientNotFoundError, RecipeNotFoundError
from .ingredients import Ingredient
from .money import Money
from .nutrition import Nutrition
from .technique import Technique
from .units import Quantity


class RecipeStep:
    """A single numbered step of a recipe."""

    def __init__(
        self,
        number: int,
        description: str,
        technique: Technique,
        minutes: int,
    ) -> None:
        if number <= 0:
            raise ValueError("Step number must be positive")
        if minutes <= 0:
            raise ValueError("Step duration must be positive")
        self._number = number
        self._description = description
        self._technique = technique
        self._minutes = minutes

    @property
    def number(self) -> int:
        """Step number."""
        return self._number

    @property
    def technique(self) -> Technique:
        """Technique used at this step."""
        return self._technique

    @property
    def minutes(self) -> int:
        """Duration of the step in minutes."""
        return self._minutes

    def perform(self, ingredient_name: str) -> str:
        """Perform the technique and return a description."""
        return self._technique.apply(ingredient_name, self._minutes)

    def describe(self) -> str:
        """Return a one-line description."""
        return (
            f"{self._number}. {self._description} "
            f"({self._minutes} min, {self._technique.name})"
        )

    def __str__(self) -> str:
        return self.describe()

    def __repr__(self) -> str:
        return f"RecipeStep({self._number}, {self._description!r})"


class RecipeIngredient:
    """An ingredient together with the required quantity."""

    def __init__(
        self,
        ingredient: Ingredient,
        quantity: Quantity,
        note: str = "",
    ) -> None:
        self._ingredient = ingredient
        self._quantity = quantity
        self._note = note

    @property
    def ingredient(self) -> Ingredient:
        """Ingredient object."""
        return self._ingredient

    @property
    def quantity(self) -> Quantity:
        """Required quantity."""
        return self._quantity

    def cost(self) -> Money:
        """Return the cost of this ingredient line."""
        return self._ingredient.price_for(self._quantity)

    def scale(self, factor: float) -> "RecipeIngredient":
        """Return a scaled copy."""
        return RecipeIngredient(self._ingredient, self._quantity * factor, self._note)

    def describe(self) -> str:
        """Return a one-line description."""
        suffix = f" - {self._note}" if self._note else ""
        return f"{self._quantity} {self._ingredient.name}{suffix}"

    def __str__(self) -> str:
        return self.describe()

    def __repr__(self) -> str:
        return f"RecipeIngredient({self._ingredient.name!r}, {self._quantity!r})"


class Recipe:
    """A recipe: ingredients, steps, servings, nutrition and allergens."""

    def __init__(
        self,
        name: str,
        servings: int = 2,
        description: str = "",
    ) -> None:
        if not name.strip():
            raise ValueError("Recipe name must not be empty")
        if servings <= 0:
            raise ValueError("Servings must be positive")
        self._name = name
        self._servings = servings
        self._description = description
        self._ingredients: list[RecipeIngredient] = []
        self._steps: list[RecipeStep] = []
        self._nutrition_per_100g = Nutrition(0.0, 0.0, 0.0, 0.0)

    @property
    def name(self) -> str:
        """Recipe name."""
        return self._name

    @property
    def servings(self) -> int:
        """Number of servings."""
        return self._servings

    def add_ingredient(self, item: RecipeIngredient) -> None:
        """Add one ingredient line."""
        self._ingredients.append(item)

    def remove_ingredient(self, name: str) -> None:
        """Remove an ingredient line by ingredient name."""
        before = len(self._ingredients)
        self._ingredients = [
            i for i in self._ingredients if i.ingredient.name != name
        ]
        if len(self._ingredients) == before:
            raise IngredientNotFoundError(name)

    def add_step(self, step: RecipeStep) -> None:
        """Add one step to the recipe."""
        expected = len(self._steps) + 1
        if step.number != expected:
            raise ValueError(f"Expected step {expected}, got {step.number}")
        self._steps.append(step)

    def set_nutrition(self, nutrition: Nutrition) -> None:
        """Set nutrition per 100 g."""
        self._nutrition_per_100g = nutrition

    def ingredient_count(self) -> int:
        """Return the number of ingredient lines."""
        return len(self._ingredients)

    def step_count(self) -> int:
        """Return the number of steps."""
        return len(self._steps)

    def total_time_minutes(self) -> int:
        """Return the total cooking time in minutes."""
        return sum(s.minutes for s in self._steps)

    def total_cost(self) -> Money:
        """Return the total cost of all ingredients."""
        if not self._ingredients:
            return Money(0)
        total = self._ingredients[0].cost()
        for item in self._ingredients[1:]:
            total = total + item.cost()
        return total

    def cost_per_serving(self) -> Money:
        """Return the cost of one serving."""
        return self.total_cost() * (1.0 / self._servings)

    def allergens(self) -> AllergenSet:
        """Return the union of all ingredient allergens."""
        result = AllergenSet()
        for item in self._ingredients:
            result = result.union(item.ingredient.allergens)
        return result

    def scale(self, factor: float) -> "Recipe":
        """Return a scaled copy with the same steps but scaled ingredients."""
        scaled = Recipe(
            f"{self._name} (x{factor:g})",
            self._servings,
            self._description,
        )
        for item in self._ingredients:
            scaled.add_ingredient(item.scale(factor))
        for step in self._steps:
            scaled.add_step(step)
        scaled.set_nutrition(self._nutrition_per_100g)
        return scaled

    def nutrition_per_serving(self) -> Nutrition:
        """Return nutrition per one serving."""
        return self._nutrition_per_100g.scale(self._servings)

    def describe(self) -> str:
        """Return a multi-line description of the recipe."""
        lines = [f"Recipe: {self._name} ({self._servings} servings)"]
        if self._description:
            lines.append(self._description)
        lines.append("Ingredients:")
        for item in self._ingredients:
            lines.append(f"  - {item.describe()}")
        lines.append("Steps:")
        for step in self._steps:
            lines.append(f"  {step.describe()}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return (
            f"{self._name} ({self._servings} servings, "
            f"{self.total_time_minutes()} min)"
        )

    def __repr__(self) -> str:
        return f"Recipe({self._name!r}, servings={self._servings})"


class RecipeBook:
    """A collection of recipes indexed by name."""

    def __init__(self, title: str = "Recipe Book") -> None:
        self._title = title
        self._recipes: dict[str, Recipe] = {}

    @property
    def title(self) -> str:
        """Title of the book."""
        return self._title

    def add(self, recipe: Recipe) -> None:
        """Add a recipe, replacing any existing one with the same name."""
        self._recipes[recipe.name.lower()] = recipe

    def find(self, name: str) -> Recipe:
        """Return a recipe by name or raise RecipeNotFoundError."""
        recipe = self._recipes.get(name.lower())
        if recipe is None:
            raise RecipeNotFoundError(name)
        return recipe

    def remove(self, name: str) -> None:
        """Remove a recipe by name."""
        if name.lower() not in self._recipes:
            raise RecipeNotFoundError(name)
        del self._recipes[name.lower()]

    def all(self) -> list[Recipe]:
        """Return a list of all recipes."""
        return list(self._recipes.values())

    def count(self) -> int:
        """Return the number of recipes."""
        return len(self._recipes)

    def find_by_allergen_free(self, forbidden: AllergenSet) -> list[Recipe]:
        """Return recipes that do not contain the forbidden allergens."""
        result: list[Recipe] = []
        for recipe in self._recipes.values():
            if not recipe.allergens().intersects(forbidden):
                result.append(recipe)
        return result

    def find_cheaper_than(self, limit: Money) -> list[Recipe]:
        """Return recipes whose total cost is at most ``limit``."""
        return [
            r for r in self._recipes.values()
            if r.total_cost().amount_minor <= limit.amount_minor
        ]

    def find_faster_than(self, minutes: int) -> list[Recipe]:
        """Return recipes that cook in at most ``minutes`` minutes."""
        return [
            r for r in self._recipes.values()
            if r.total_time_minutes() <= minutes
        ]

    def total_cost(self) -> Money:
        """Return the sum of all recipes' costs."""
        recipes = self.all()
        if not recipes:
            return Money(0)
        total = recipes[0].total_cost()
        for r in recipes[1:]:
            total = total + r.total_cost()
        return total

    def __len__(self) -> int:
        return len(self._recipes)

    def __str__(self) -> str:
        return f"{self._title} ({self.count()} recipes)"

    def __repr__(self) -> str:
        return f"RecipeBook({self._title!r}, {self.count()})"


class RecipeAnalyzer:
    """Analysis helpers over Recipe instances."""

    def __init__(self, recipe: Recipe) -> None:
        self._recipe = recipe

    def ingredient_names(self) -> list[str]:
        """Return ingredient names in order."""
        return [i.ingredient.name for i in self._recipe._ingredients]

    def most_expensive_ingredient(self) -> str:
        """Return the name of the most expensive ingredient."""
        if not self._recipe._ingredients:
            raise IngredientNotFoundError("Recipe has no ingredients")
        expensive = max(
            self._recipe._ingredients,
            key=lambda i: i.cost().amount_minor,
        )
        return expensive.ingredient.name

    def average_step_minutes(self) -> float:
        """Return the average duration of a step, or 0 if there are none."""
        if not self._recipe._steps:
            return 0.0
        return self._recipe.total_time_minutes() / len(self._recipe._steps)

    def cost_breakdown(self) -> dict[str, int]:
        """Return a mapping from ingredient name to cost in minor units."""
        return {
            i.ingredient.name: i.cost().amount_minor
            for i in self._recipe._ingredients
        }

    def is_low_calorie(self, threshold_kcal: float = 200.0) -> bool:
        """Return True if the recipe has fewer than ``threshold_kcal`` per serving."""
        return self._recipe.nutrition_per_serving().kcal() < threshold_kcal

    def technique_count(self) -> int:
        """Return how many distinct techniques are used."""
        return len({s.technique.name for s in self._recipe._steps})

    def summary(self) -> str:
        """Return a short analysis summary."""
        return (
            f"{self._recipe.name}: "
            f"{self._recipe.ingredient_count()} ingredients, "
            f"{self._recipe.step_count()} steps, "
            f"cost {self._recipe.total_cost()}"
        )
