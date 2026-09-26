"""Tests for analytics."""
import pytest

from lab2.src.analytics import (
    CostCalculator,
    ExpenseTracker,
    FuelConsumption,
    Metric,
    MetricsReport,
    PerformanceMetric,
    ProfitAnalyzer,
    ReportGenerator,
    TaxCalculator,
    TrafficInfo,
)
from lab2.src.exceptions import InvalidQuantityError
from lab2.src.ingredients import Vegetable
from lab2.src.money import Money
from lab2.src.recipes import Recipe, RecipeIngredient, RecipeStep
from lab2.src.technique import Boil
from lab2.src.units import Quantity, Unit


def _recipe(name: str = "Soup", servings: int = 4):
    r = Recipe(name, servings)
    tomato = Vegetable("Tomato", Unit.KILOGRAM, Money.from_major(150.0), 5, 9)
    r.add_ingredient(RecipeIngredient(tomato, Quantity(0.5, Unit.KILOGRAM)))
    r.add_step(RecipeStep(1, "Boil", Boil(), 15))
    return r


class TestCostCalculator:
    def test_negative_tax(self):
        with pytest.raises(InvalidQuantityError):
            CostCalculator(tax_percent=-1)

    def test_base_cost(self):
        assert CostCalculator().base_cost(_recipe()) == Money.from_major(75.0)

    def test_cost_with_tax(self):
        assert CostCalculator(tax_percent=20).cost_with_tax(_recipe()) == Money.from_major(90.0)

    def test_cost_per_serving_with_tax(self):
        cc = CostCalculator(tax_percent=20)
        assert cc.cost_per_serving_with_tax(_recipe()) == Money.from_major(22.50)

    def test_compare(self):
        a = _recipe("A")
        b = _recipe("B")
        assert CostCalculator().compare(a, b) == "equal"

    def test_describe(self):
        assert "20" in CostCalculator(tax_percent=20).describe()


class TestProfitAnalyzer:
    def test_bad_target(self):
        with pytest.raises(InvalidQuantityError):
            ProfitAnalyzer(target_margin=1.0)

    def test_suggested_price(self):
        pa = ProfitAnalyzer(target_margin=0.25)
        assert pa.suggested_price(_recipe(), Money.from_major(75)) == Money.from_major(100)

    def test_profit_and_margin(self):
        pa = ProfitAnalyzer()
        cost = Money.from_major(75)
        price = Money.from_major(100)
        assert pa.profit(cost, price) == Money.from_major(25)
        assert pa.margin(cost, price) == pytest.approx(0.25)

    def test_margin_zero_price(self):
        assert ProfitAnalyzer().margin(Money(100), Money(0)) == 0.0

    def test_meets_target(self):
        pa = ProfitAnalyzer(target_margin=0.20)
        assert pa.meets_target(Money.from_major(75), Money.from_major(100))
        assert not pa.meets_target(Money.from_major(90), Money.from_major(100))

    def test_describe(self):
        assert "ProfitAnalyzer" in ProfitAnalyzer().describe()


class TestTaxCalculator:
    def test_negative(self):
        with pytest.raises(InvalidQuantityError):
            TaxCalculator(-1)

    def test_apply_of_strip(self):
        tc = TaxCalculator(20)
        assert tc.apply(Money.from_major(100)) == Money.from_major(120)
        assert tc.of(Money.from_major(100)) == Money.from_major(20)
        assert tc.strip(Money.from_major(120)) == Money.from_major(100)

    def test_describe(self):
        assert "20" in TaxCalculator(20).describe()


class TestMetrics:
    def test_metric_helpers(self):
        m = Metric("revenue", 500.0, "RUB")
        assert m.is_positive()
        assert "revenue" in m.as_str()

    def test_metrics_report(self):
        rep = MetricsReport("Daily")
        rep.add(Metric("a", 1.0))
        rep.add(Metric("b", 3.0))
        assert rep.total() == 4.0
        assert rep.average() == 2.0
        assert rep.positive_count() == 2
        assert rep.find("a") is not None
        assert rep.find("z") is None

    def test_empty_report(self):
        rep = MetricsReport("Empty")
        assert rep.average() == 0.0
        assert "Empty" in rep.describe()

    def test_performance_metric(self):
        pm = PerformanceMetric("speed")
        pm.record(10)
        pm.record(20)
        assert pm.latest() == 20
        assert pm.average() == 15.0
        assert pm.peak() == 20
        assert "speed" in pm.describe()

    def test_performance_metric_empty(self):
        pm = PerformanceMetric("x")
        assert pm.latest() == 0.0
        assert pm.average() == 0.0
        assert pm.peak() == 0.0


class TestMisc:
    def test_fuel_consumption(self):
        fc = FuelConsumption(8.0)
        assert fc.litres_for(150) == pytest.approx(12.0)
        assert fc.cost_for(150, Money.from_major(2.0)) == Money.from_major(24.0)

    def test_fuel_bad(self):
        with pytest.raises(InvalidQuantityError):
            FuelConsumption(0)

    def test_traffic(self):
        t = TrafficInfo(45.0, 90.0)
        assert t.travel_hours() == 2.0
        assert not t.is_slow()

    def test_traffic_slow(self):
        t = TrafficInfo(15.0, 30.0)
        assert t.is_slow()

    def test_traffic_zero_distance(self):
        assert TrafficInfo(60.0, 0.0).travel_hours() == 0.0

    def test_expense_tracker(self):
        ex = ExpenseTracker()
        ex.add("rent", Money.from_major(1000))
        ex.add("rent", Money.from_major(500))
        ex.add("food", Money.from_major(300))
        assert ex.category_count() == 2
        assert ex.category_total("rent") == Money.from_major(1500)
        assert ex.total() == Money.from_major(1800)
        assert ex.top_category() == "rent"
        assert "ExpenseTracker" in ex.describe()

    def test_expense_tracker_empty(self):
        assert ExpenseTracker().top_category() == ""
        assert ExpenseTracker().total().is_zero()

    def test_report_generator(self):
        rg = ReportGenerator("Daily")
        rg.add_line("hello")
        rg.add_metric(Metric("revenue", 100.0))
        assert rg.line_count() == 2
        assert not rg.is_empty()
        text = rg.render()
        assert "Daily" in text
        assert "hello" in text

    def test_report_generator_empty(self):
        assert ReportGenerator("X").is_empty()
        assert ReportGenerator("X").render() == "X"
