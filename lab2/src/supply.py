"""Supply chain: suppliers, purchase orders, deliveries, invoices, inventory."""
from __future__ import annotations

from datetime import date

from .exceptions import (
    InsufficientFundsError,
    InvalidQuantityError,
    OrderAlreadyClosedError,
    SupplierUnavailableError,
)
from .ingredients import Ingredient, IngredientLot
from .money import Money
from .units import Quantity


class Supplier:
    """A company that supplies ingredients."""

    def __init__(
        self,
        name: str,
        contact_email: str,
        min_order: Money,
        rating: float = 5.0,
    ) -> None:
        if not name.strip():
            raise InvalidQuantityError("Supplier name must not be empty")
        self._name = name
        self._contact_email = contact_email
        self._min_order = min_order
        self._rating = max(0.0, min(5.0, rating))
        self._available = True
        self._catalog: dict[str, Money] = {}

    @property
    def name(self) -> str:
        """Supplier name."""
        return self._name

    @property
    def rating(self) -> float:
        """Supplier rating 0-5."""
        return self._rating

    def is_available(self) -> bool:
        """Return True if the supplier can take new orders."""
        return self._available

    def suspend(self) -> None:
        """Temporarily suspend the supplier."""
        self._available = False

    def resume(self) -> None:
        """Return the supplier to service."""
        self._available = True

    def add_to_catalog(self, ingredient: Ingredient, unit_price: Money) -> None:
        """Add or replace an ingredient in the catalog."""
        self._catalog[ingredient.name] = unit_price

    def price_for(self, ingredient: Ingredient) -> Money:
        """Return the catalog price or the ingredient's default price."""
        return self._catalog.get(ingredient.name, ingredient._price_per_unit)

    def has(self, ingredient: Ingredient) -> bool:
        """Return True if the ingredient is in the catalog."""
        return ingredient.name in self._catalog

    def catalog_size(self) -> int:
        """Return the number of catalog entries."""
        return len(self._catalog)

    def can_accept(self, total: Money) -> bool:
        """Return True if the order total meets the minimum."""
        return total.amount_minor >= self._min_order.amount_minor

    def __str__(self) -> str:
        return (
            f"Supplier {self._name} (rating {self._rating:.1f}, "
            f"{self.catalog_size()} items)"
        )

    def __repr__(self) -> str:
        return f"Supplier({self._name!r})"


class PurchaseOrderLine:
    """A single line in a purchase order."""

    def __init__(
        self,
        ingredient: Ingredient,
        quantity: Quantity,
        unit_price: Money,
    ) -> None:
        if quantity.amount <= 0:
            raise InvalidQuantityError("Order line quantity must be positive")
        self._ingredient = ingredient
        self._quantity = quantity
        self._unit_price = unit_price

    @property
    def ingredient(self) -> Ingredient:
        """Ingredient being ordered."""
        return self._ingredient

    @property
    def quantity(self) -> Quantity:
        """Ordered quantity."""
        return self._quantity

    def line_total(self) -> Money:
        """Return unit price x quantity converted to the ingredient's unit."""
        converted = self._quantity.to(self._ingredient.unit)
        return self._unit_price * converted.amount

    def describe(self) -> str:
        """Return a one-line description."""
        return f"{self._quantity} {self._ingredient.name} @ {self._unit_price}"

    def __str__(self) -> str:
        return self.describe()


class PurchaseOrder:
    """A purchase order for a supplier."""

    STATUS_OPEN = "open"
    STATUS_SENT = "sent"
    STATUS_RECEIVED = "received"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, supplier: Supplier, order_date: date) -> None:
        self._supplier = supplier
        self._order_date = order_date
        self._lines: list[PurchaseOrderLine] = []
        self._status = self.STATUS_OPEN

    @property
    def supplier(self) -> Supplier:
        """Supplier for this order."""
        return self._supplier

    @property
    def status(self) -> str:
        """Current status."""
        return self._status

    def add_line(self, line: PurchaseOrderLine) -> None:
        """Add a line; raise if the order is not open."""
        if self._status != self.STATUS_OPEN:
            raise OrderAlreadyClosedError(
                f"Cannot modify order in status {self._status}"
            )
        self._lines.append(line)

    def total(self) -> Money:
        """Return the total cost of all lines."""
        if not self._lines:
            return Money(0)
        total = self._lines[0].line_total()
        for line in self._lines[1:]:
            total = total + line.line_total()
        return total

    def send(self) -> None:
        """Transition the order to 'sent'."""
        if self._status != self.STATUS_OPEN:
            raise OrderAlreadyClosedError("Only open orders can be sent")
        if not self._supplier.is_available():
            raise SupplierUnavailableError(
                f"{self._supplier.name} is not available"
            )
        if not self._supplier.can_accept(self.total()):
            raise InsufficientFundsError(
                "Order total is below the supplier's minimum"
            )
        self._status = self.STATUS_SENT

    def receive(self) -> None:
        """Transition the order to 'received'."""
        if self._status != self.STATUS_SENT:
            raise OrderAlreadyClosedError("Only sent orders can be received")
        self._status = self.STATUS_RECEIVED

    def cancel(self) -> None:
        """Cancel the order unless it has been received."""
        if self._status == self.STATUS_RECEIVED:
            raise OrderAlreadyClosedError("Cannot cancel a received order")
        self._status = self.STATUS_CANCELLED

    def line_count(self) -> int:
        """Return the number of lines."""
        return len(self._lines)

    def describe(self) -> str:
        """Return a multi-line description."""
        lines = [
            f"PurchaseOrder to {self._supplier.name} "
            f"({self._status}), total {self.total()}"
        ]
        for line in self._lines:
            lines.append(f"  {line.describe()}")
        return "\n".join(lines)


class Delivery:
    """A physical delivery of one purchase order."""

    def __init__(
        self,
        order: PurchaseOrder,
        delivery_date: date,
        address: str,
    ) -> None:
        self._order = order
        self._delivery_date = delivery_date
        self._address = address
        self._delivered = False

    @property
    def order(self) -> PurchaseOrder:
        """Order being delivered."""
        return self._order

    @property
    def delivery_date(self) -> date:
        """Scheduled date."""
        return self._delivery_date

    def mark_delivered(self) -> None:
        """Mark the delivery as completed and set the order to 'received'."""
        self._delivered = True
        self._order.receive()

    def is_delivered(self) -> bool:
        """Return True if the delivery was completed."""
        return self._delivered

    def late_by_days(self, today: date) -> int:
        """Return how many days late the delivery is (0 if on time)."""
        if self._delivered:
            return 0
        return max(0, (today - self._delivery_date).days)

    def describe(self) -> str:
        status = "delivered" if self._delivered else "pending"
        return f"Delivery to {self._address} on {self._delivery_date} [{status}]"


class Invoice:
    """An invoice for a purchase order."""

    STATUS_ISSUED = "issued"
    STATUS_PAID = "paid"

    def __init__(self, order: PurchaseOrder, invoice_number: str) -> None:
        self._order = order
        self._invoice_number = invoice_number
        self._status = self.STATUS_ISSUED
        self._payments: list[Money] = []

    @property
    def invoice_number(self) -> str:
        """Invoice number."""
        return self._invoice_number

    @property
    def status(self) -> str:
        """Current status."""
        return self._status

    def total(self) -> Money:
        """Return the total from the order."""
        return self._order.total()

    def paid_amount(self) -> Money:
        """Return the sum of payments made so far."""
        if not self._payments:
            return Money(0)
        total = self._payments[0]
        for p in self._payments[1:]:
            total = total + p
        return total

    def remaining(self) -> Money:
        """Return how much is still owed."""
        return self.total() - self.paid_amount()

    def pay(self, amount: Money) -> None:
        """Register a payment; raises on overpayment."""
        if amount.amount_minor > self.remaining().amount_minor:
            raise InsufficientFundsError("Overpayment not allowed")
        self._payments.append(amount)
        if self.paid_amount().amount_minor == self.total().amount_minor:
            self._status = self.STATUS_PAID

    def is_paid(self) -> bool:
        """Return True if the invoice has been fully paid."""
        return self._status == self.STATUS_PAID

    def describe(self) -> str:
        """Return a one-line description."""
        return (
            f"Invoice {self._invoice_number} [{self._status}], "
            f"total {self.total()}, remaining {self.remaining()}"
        )


class Inventory:
    """A collection of ingredient lots with reorder logic."""

    def __init__(self) -> None:
        self._lots: list[IngredientLot] = []
        self._reorder_levels: dict[str, float] = {}

    def add_lot(self, lot: IngredientLot) -> None:
        """Add a lot to the inventory."""
        self._lots.append(lot)

    def set_reorder_level(self, ingredient_name: str, quantity: float) -> None:
        """Set the reorder threshold for an ingredient."""
        self._reorder_levels[ingredient_name] = quantity

    def total_quantity(self, ingredient_name: str) -> float:
        """Return the total amount of an ingredient across all lots."""
        total = 0.0
        for lot in self._lots:
            if lot.ingredient.name == ingredient_name:
                total += lot.quantity.amount
        return total

    def needs_reorder(self, ingredient_name: str) -> bool:
        """Return True if the total quantity is below the reorder level."""
        level = self._reorder_levels.get(ingredient_name, 0.0)
        return self.total_quantity(ingredient_name) < level

    def expired_lots(self, today: date) -> list[IngredientLot]:
        """Return all lots that have expired."""
        return [lot for lot in self._lots if lot.is_expired(today)]

    def discard_expired(self, today: date) -> int:
        """Remove expired lots; return how many were discarded."""
        expired = self.expired_lots(today)
        for lot in expired:
            self._lots.remove(lot)
        return len(expired)

    def lot_count(self) -> int:
        """Return the number of lots."""
        return len(self._lots)

    def describe(self) -> str:
        """Return a one-line description."""
        return (
            f"Inventory: {self.lot_count()} lots, "
            f"reorder rules for {len(self._reorder_levels)} ingredients"
        )
