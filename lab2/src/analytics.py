"""Analytics: cost, profit, tax and KPI calculations for the culinary domain."""
from __future__ import annotations

from dataclasses import dataclass, field

from .exceptions import InvalidQuantityError
from .money import Money
from .recipes import Recipe

DEFAULT_TAX_PERCENT = 20.0
DEFAULT_PROFIT_MARGIN = 0.25


class CostCalculator:
    """Computes costs of recipes and menus."""

    def __init__(self, tax_percent: float = DEFAULT_TAX_PERCENT) -> None:
        if tax_percent < 0:
            raise InvalidQuantityError("Tax percent must be non-negative")
        self._tax_percent = tax_percent

    def base_cost(self, recipe: Recipe) -> Money:
        """Return the raw ingredient cost of a recipe."""
        return recipe.total_cost()

    def cost_with_tax(self, recipe: Recipe) -> Money:
        """Return the recipe cost including tax."""
        factor = 1 + self._tax_percent / 100.0
        return recipe.total_cost() * factor

    def cost_per_serving_with_tax(self, recipe: Recipe) -> Money:
        """Return the taxed cost of one serving."""
        per_serving = self.cost_with_tax(recipe)
        return per_serving * (1.0 / recipe.servings)

    def compare(self, recipe_a: Recipe, recipe_b: Recipe) -> str:
        """Return the name of the cheaper recipe."""
        a = recipe_a.total_cost().amount_minor
        b = recipe_b.total_cost().amount_minor
        if a < b:
            return recipe_a.name
        if b < a:
            return recipe_b.name
        return "equal"

    def describe(self) -> str:
        return f"CostCalculator (tax {self._tax_percent}%)"


class ProfitAnalyzer:
    """Calculates profit and margins for recipes and menus."""

    def __init__(self, target_margin: float = DEFAULT_PROFIT_MARGIN) -> None:
        if not 0 <= target_margin < 1:
            raise InvalidQuantityError("Target margin must be in [0, 1)")
        self._target_margin = target_margin

    def suggested_price(self, recipe: Recipe, cost: Money) -> Money:
        """Return a price that yields the target margin."""
        factor = 1.0 / (1.0 - self._target_margin)
        return cost * factor

    def profit(self, cost: Money, price: Money) -> Money:
        """Return profit = price - cost."""
        return price - cost

    def margin(self, cost: Money, price: Money) -> float:
        """Return margin = (price - cost) / price, 0 if price is zero."""
        if price.is_zero():
            return 0.0
        return (price.amount_minor - cost.amount_minor) / price.amount_minor

    def meets_target(self, cost: Money, price: Money) -> bool:
        """Return True if margin meets the target."""
        return self.margin(cost, price) >= self._target_margin

    def describe(self) -> str:
        return f"ProfitAnalyzer (target margin {self._target_margin:.0%})"


class TaxCalculator:
    """Applies a tax rate to monetary amounts."""

    def __init__(self, rate_percent: float) -> None:
        if rate_percent < 0:
            raise InvalidQuantityError("Tax rate must be non-negative")
        self._rate_percent = rate_percent

    @property
    def rate_percent(self) -> float:
        """Tax rate in percent."""
        return self._rate_percent

    def apply(self, amount: Money) -> Money:
        """Return the amount with tax added."""
        return amount * (1 + self._rate_percent / 100.0)

    def of(self, amount: Money) -> Money:
        """Return the tax portion of the amount."""
        return amount * (self._rate_percent / 100.0)

    def strip(self, amount_with_tax: Money) -> Money:
        """Return the amount without tax."""
        factor = 1 + self._rate_percent / 100.0
        return amount_with_tax * (1.0 / factor)

    def describe(self) -> str:
        return f"TaxCalculator ({self._rate_percent}%)"


@dataclass
class Metric:
    """A single named metric with a numeric value."""

    name: str
    value: float
    unit: str = ""

    def is_positive(self) -> bool:
        """Return True if the value is strictly positive."""
        return self.value > 0

    def as_str(self) -> str:
        """Return a formatted string."""
        suffix = f" {self.unit}" if self.unit else ""
        return f"{self.name}: {self.value:g}{suffix}"


@dataclass
class MetricsReport:
    """A bundle of named metrics with basic aggregation."""

    title: str
    metrics: list[Metric] = field(default_factory=list)

    def add(self, metric: Metric) -> None:
        """Add a metric."""
        self.metrics.append(metric)

    def find(self, name: str) -> Metric | None:
        """Return a metric by name or None."""
        for m in self.metrics:
            if m.name == name:
                return m
        return None

    def total(self) -> float:
        """Return the sum of all values."""
        return sum(m.value for m in self.metrics)

    def average(self) -> float:
        """Return the average value, 0 if there are no metrics."""
        if not self.metrics:
            return 0.0
        return self.total() / len(self.metrics)

    def positive_count(self) -> int:
        """Return how many metrics have a strictly positive value."""
        return sum(1 for m in self.metrics if m.is_positive())

    def describe(self) -> str:
        return f"MetricsReport '{self.title}' ({len(self.metrics)} metrics)"


class PerformanceMetric:
    """A simple time-series of performance values."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._values: list[float] = []

    @property
    def name(self) -> str:
        """Metric name."""
        return self._name

    def record(self, value: float) -> None:
        """Append a value."""
        self._values.append(value)

    def latest(self) -> float:
        """Return the latest value, 0 if there are none."""
        if not self._values:
            return 0.0
        return self._values[-1]

    def average(self) -> float:
        """Return the average value, 0 if there are none."""
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)

    def peak(self) -> float:
        """Return the maximum value, 0 if there are none."""
        if not self._values:
            return 0.0
        return max(self._values)

    def describe(self) -> str:
        return (
            f"PerformanceMetric '{self._name}' "
            f"({len(self._values)} records, avg {self.average():.2f})"
        )


class FuelConsumption:
    """Tracks fuel consumption per distance for delivery vehicles."""

    def __init__(self, litres_per_100km: float) -> None:
        if litres_per_100km <= 0:
            raise InvalidQuantityError("Consumption must be positive")
        self._litres_per_100km = litres_per_100km

    def litres_for(self, distance_km: float) -> float:
        """Return litres needed for a distance."""
        return self._litres_per_100km * distance_km / 100.0

    def cost_for(self, distance_km: float, price_per_litre: Money) -> Money:
        """Return money spent on fuel for a trip."""
        return price_per_litre * self.litres_for(distance_km)

    def describe(self) -> str:
        return f"FuelConsumption ({self._litres_per_100km} L/100km)"


class TrafficInfo:
    """Average speed on a route."""

    def __init__(self, average_speed_kmh: float, distance_km: float) -> None:
        if average_speed_kmh <= 0:
            raise InvalidQuantityError("Average speed must be positive")
        if distance_km < 0:
            raise InvalidQuantityError("Distance must be non-negative")
        self._average_speed_kmh = average_speed_kmh
        self._distance_km = distance_km

    def travel_hours(self) -> float:
        """Return estimated travel time in hours."""
        if self._distance_km == 0:
            return 0.0
        return self._distance_km / self._average_speed_kmh

    def is_slow(self) -> bool:
        """Return True if traffic is below 20 km/h."""
        return self._average_speed_kmh < 20.0

    def describe(self) -> str:
        return (
            f"TrafficInfo (avg {self._average_speed_kmh} km/h, "
            f"{self._distance_km} km -> {self.travel_hours():.2f} h)"
        )


class ExpenseTracker:
    """Accumulates expenses by category."""

    def __init__(self) -> None:
        self._by_category: dict[str, Money] = {}

    def add(self, category: str, amount: Money) -> None:
        """Add an expense to a category."""
        current = self._by_category.get(category)
        if current is None:
            self._by_category[category] = amount
        else:
            self._by_category[category] = current + amount

    def total(self) -> Money:
        """Return the sum of all expenses."""
        total: Money | None = None
        for amount in self._by_category.values():
            total = amount if total is None else total + amount
        return total if total is not None else Money(0)

    def category_total(self, category: str) -> Money:
        """Return the total for one category."""
        return self._by_category.get(category, Money(0))

    def category_count(self) -> int:
        """Return how many categories have been used."""
        return len(self._by_category)

    def top_category(self) -> str:
        """Return the category with the largest total, or '' if empty."""
        if not self._by_category:
            return ""
        return max(
            self._by_category.items(),
            key=lambda kv: kv[1].amount_minor,
        )[0]

    def describe(self) -> str:
        return (
            f"ExpenseTracker ({self.category_count()} categories, "
            f"total {self.total()})"
        )


class ReportGenerator:
    """Builds human-readable reports from metrics."""

    def __init__(self, title: str) -> None:
        self._title = title
        self._lines: list[str] = []

    def add_line(self, line: str) -> None:
        """Append a line to the report."""
        self._lines.append(line)

    def add_metric(self, metric: Metric) -> None:
        """Append a metric line to the report."""
        self._lines.append(metric.as_str())

    def line_count(self) -> int:
        """Return the number of lines."""
        return len(self._lines)

    def is_empty(self) -> bool:
        """Return True if the report has no lines."""
        return not self._lines

    def render(self) -> str:
        """Return the full report as text."""
        header = self._title
        body = "\n".join(self._lines)
        return f"{header}\n{body}" if body else header
