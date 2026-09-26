"""Tests for the custom exceptions module."""
import pytest

from lab2.src.exceptions import (
    AllergenConflictError,
    CertificateExpiredError,
    CulinaryException,
    EquipmentBrokenError,
    EquipmentUnavailableError,
    IngredientNotFoundError,
    InsufficientFundsError,
    InsufficientIngredientError,
    InvalidMenuItemError,
    InvalidQuantityError,
    InvalidScheduleError,
    InvalidUnitError,
    OrderAlreadyClosedError,
    OvercookedError,
    PaymentFailedError,
    RecipeNotFoundError,
    ReservationConflictError,
    SupplierUnavailableError,
    TableNotFoundError,
)


ALL_EXCEPTIONS = [
    RecipeNotFoundError,
    IngredientNotFoundError,
    InsufficientIngredientError,
    InvalidQuantityError,
    InvalidUnitError,
    AllergenConflictError,
    OvercookedError,
    EquipmentUnavailableError,
    EquipmentBrokenError,
    ReservationConflictError,
    TableNotFoundError,
    OrderAlreadyClosedError,
    PaymentFailedError,
    InsufficientFundsError,
    InvalidMenuItemError,
    SupplierUnavailableError,
    InvalidScheduleError,
    CertificateExpiredError,
]


class TestExceptions:
    def test_base_is_exception(self):
        assert issubclass(CulinaryException, Exception)

    def test_all_inherit_from_base(self):
        for exc_cls in ALL_EXCEPTIONS:
            assert issubclass(exc_cls, CulinaryException)

    @pytest.mark.parametrize("exc_cls", ALL_EXCEPTIONS)
    def test_raise_and_catch(self, exc_cls):
        with pytest.raises(exc_cls):
            raise exc_cls("boom")

    def test_message_preserved(self):
        try:
            raise RecipeNotFoundError("Pizza")
        except RecipeNotFoundError as e:
            assert str(e) == "Pizza"
