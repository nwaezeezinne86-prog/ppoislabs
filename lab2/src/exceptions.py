"""Custom exceptions for the culinary domain."""


class CulinaryException(Exception):
    """Base exception for the culinary domain."""


class RecipeNotFoundError(CulinaryException):
    """Raised when a recipe cannot be found by name or id."""


class IngredientNotFoundError(CulinaryException):
    """Raised when an ingredient is missing from the catalog or storage."""


class InsufficientIngredientError(CulinaryException):
    """Raised when there is not enough of an ingredient to cook a dish."""


class InvalidQuantityError(CulinaryException):
    """Raised when a quantity value is not positive or is malformed."""


class InvalidUnitError(CulinaryException):
    """Raised when a measurement unit is not supported."""


class AllergenConflictError(CulinaryException):
    """Raised when a dish contains an allergen forbidden for the customer."""


class OvercookedError(CulinaryException):
    """Raised when a cooking process exceeds its allowed duration."""


class EquipmentUnavailableError(CulinaryException):
    """Raised when required equipment is already in use or broken."""


class EquipmentBrokenError(CulinaryException):
    """Raised when a piece of equipment is marked as out of service."""


class ReservationConflictError(CulinaryException):
    """Raised when two reservations overlap for the same table."""


class TableNotFoundError(CulinaryException):
    """Raised when a table cannot be found in a restaurant."""


class OrderAlreadyClosedError(CulinaryException):
    """Raised when an attempt is made to modify a closed order."""


class PaymentFailedError(CulinaryException):
    """Raised when a payment transaction fails."""


class InsufficientFundsError(CulinaryException):
    """Raised when a customer or account does not have enough money."""


class InvalidMenuItemError(CulinaryException):
    """Raised when a menu item cannot be added to a menu."""


class SupplierUnavailableError(CulinaryException):
    """Raised when a supplier cannot fulfil a delivery request."""


class InvalidScheduleError(CulinaryException):
    """Raised when a shift assignment violates the schedule rules."""


class CertificateExpiredError(CulinaryException):
    """Raised when an expired certificate is presented."""
