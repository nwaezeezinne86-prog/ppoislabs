"""Tests for supply chain."""
from datetime import date

import pytest

from lab2.src.exceptions import (
    InsufficientFundsError,
    InvalidQuantityError,
    OrderAlreadyClosedError,
    SupplierUnavailableError,
)
from lab2.src.ingredients import Ingredient, IngredientLot, Vegetable
from lab2.src.money import Money
from lab2.src.supply import (
    Delivery,
    Inventory,
    Invoice,
    PurchaseOrder,
    PurchaseOrderLine,
    Supplier,
)
from lab2.src.units import Quantity, Unit


def _tomato():
    return Vegetable("Tomato", Unit.KILOGRAM, Money.from_major(150.0), 5, 9)


def _supplier():
    s = Supplier("FreshFood", "a@b.c", Money.from_major(10))
    s.add_to_catalog(_tomato(), Money.from_major(140.0))
    return s


def _order():
    sup = _supplier()
    order = PurchaseOrder(sup, date(2026, 9, 26))
    order.add_line(PurchaseOrderLine(
        _tomato(), Quantity(10, Unit.KILOGRAM), Money.from_major(140)
    ))
    return order


class TestSupplier:
    def test_empty_name(self):
        with pytest.raises(InvalidQuantityError):
            Supplier("", "x", Money(0))

    def test_suspend_resume(self):
        s = _supplier()
        s.suspend()
        assert not s.is_available()
        s.resume()
        assert s.is_available()

    def test_catalog(self):
        s = _supplier()
        assert s.has(_tomato())
        assert s.catalog_size() == 1

    def test_price_fallback(self):
        s = Supplier("X", "x", Money(0))
        ing = Ingredient("X", Unit.GRAM, Money.from_major(5))
        assert s.price_for(ing) == Money.from_major(5)

    def test_can_accept_minimum(self):
        s = _supplier()
        assert s.can_accept(Money.from_major(100))
        assert not s.can_accept(Money.from_major(1))

    def test_str_and_repr(self):
        s = _supplier()
        assert "FreshFood" in str(s)
        assert "Supplier" in repr(s)


class TestPurchaseOrderLine:
    def test_zero_quantity(self):
        with pytest.raises(InvalidQuantityError):
            PurchaseOrderLine(_tomato(), Quantity(0, Unit.KILOGRAM), Money(0))

    def test_line_total(self):
        line = PurchaseOrderLine(_tomato(), Quantity(2, Unit.KILOGRAM),
                                 Money.from_major(140))
        assert line.line_total() == Money.from_major(280)

    def test_describe_str(self):
        line = PurchaseOrderLine(_tomato(), Quantity(2, Unit.KILOGRAM),
                                 Money.from_major(140))
        assert "Tomato" in line.describe()
        assert str(line) == line.describe()


class TestPurchaseOrder:
    def test_add_line_after_send(self):
        order = _order()
        order.send()
        with pytest.raises(OrderAlreadyClosedError):
            order.add_line(PurchaseOrderLine(_tomato(), Quantity(1, Unit.KILOGRAM), Money(0)))

    def test_total_empty(self):
        order = PurchaseOrder(_supplier(), date(2026, 9, 26))
        assert order.total().is_zero()

    def test_total(self):
        assert _order().total() == Money.from_major(1400)

    def test_send_unavailable(self):
        sup = _supplier()
        sup.suspend()
        order = PurchaseOrder(sup, date(2026, 9, 26))
        order.add_line(PurchaseOrderLine(_tomato(), Quantity(1, Unit.KILOGRAM), Money(0)))
        with pytest.raises(SupplierUnavailableError):
            order.send()

    def test_send_below_min(self):
        sup = Supplier("X", "x", Money.from_major(10000))
        order = PurchaseOrder(sup, date(2026, 9, 26))
        order.add_line(PurchaseOrderLine(_tomato(), Quantity(1, Unit.KILOGRAM), Money.from_major(10)))
        with pytest.raises(InsufficientFundsError):
            order.send()

    def test_receive_requires_sent(self):
        with pytest.raises(OrderAlreadyClosedError):
            _order().receive()

    def test_cancel(self):
        order = _order()
        order.cancel()
        assert order.status == PurchaseOrder.STATUS_CANCELLED

    def test_cancel_received(self):
        order = _order()
        order.send()
        order.receive()
        with pytest.raises(OrderAlreadyClosedError):
            order.cancel()

    def test_describe(self):
        assert "FreshFood" in _order().describe()


class TestDelivery:
    def test_mark_delivered(self):
        order = _order()
        order.send()
        d = Delivery(order, date(2026, 9, 28), "Kitchen")
        d.mark_delivered()
        assert d.is_delivered()
        assert order.status == PurchaseOrder.STATUS_RECEIVED

    def test_late_days(self):
        order = _order()
        order.send()
        d = Delivery(order, date(2026, 9, 28), "Kitchen")
        assert d.late_by_days(date(2026, 9, 30)) == 2
        d.mark_delivered()
        assert d.late_by_days(date(2026, 9, 30)) == 0

    def test_describe(self):
        order = _order()
        d = Delivery(order, date(2026, 9, 28), "Kitchen")
        assert "Kitchen" in d.describe()


class TestInvoice:
    def test_pay_partial(self):
        inv = Invoice(_order(), "INV-1")
        inv.pay(Money.from_major(500))
        assert not inv.is_paid()
        assert inv.remaining() == Money.from_major(900)

    def test_pay_full(self):
        inv = Invoice(_order(), "INV-1")
        inv.pay(Money.from_major(1400))
        assert inv.is_paid()

    def test_overpayment(self):
        inv = Invoice(_order(), "INV-1")
        with pytest.raises(InsufficientFundsError):
            inv.pay(Money.from_major(100000))

    def test_describe(self):
        assert "INV-1" in Invoice(_order(), "INV-1").describe()


class TestInventory:
    def test_add_lot(self):
        inv = Inventory()
        inv.add_lot(IngredientLot(_tomato(), Quantity(5, Unit.KILOGRAM), date(2026, 10, 1)))
        assert inv.lot_count() == 1

    def test_total_quantity(self):
        inv = Inventory()
        inv.add_lot(IngredientLot(_tomato(), Quantity(5, Unit.KILOGRAM), date(2026, 10, 1)))
        inv.add_lot(IngredientLot(_tomato(), Quantity(3, Unit.KILOGRAM), date(2026, 10, 5)))
        assert inv.total_quantity("Tomato") == 8

    def test_reorder(self):
        inv = Inventory()
        inv.set_reorder_level("Tomato", 10)
        assert inv.needs_reorder("Tomato")
        inv.add_lot(IngredientLot(_tomato(), Quantity(15, Unit.KILOGRAM), date(2026, 10, 1)))
        assert not inv.needs_reorder("Tomato")

    def test_expired_lots(self):
        inv = Inventory()
        inv.add_lot(IngredientLot(_tomato(), Quantity(1, Unit.KILOGRAM), date(2026, 1, 1)))
        today = date(2026, 9, 26)
        assert len(inv.expired_lots(today)) == 1
        assert inv.discard_expired(today) == 1
        assert inv.lot_count() == 0

    def test_describe(self):
        assert "Inventory" in Inventory().describe()
