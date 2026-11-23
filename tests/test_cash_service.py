from decimal import Decimal

import pytest

from kmportfolio_tracker.errors import InvalidAmountError
from kmportfolio_tracker.services import cash_service


# Check that depositing money increases the cash balance.
def test_deposit_increases_cash_balance(empty_db):
    cash_service.deposit(Decimal(1000))
    # $0 + $1,000 = $1,000
    assert cash_service.get_balance() == Decimal("1000.00")

# Check that deposits round half up to the nearest cent.
def test_deposit_rounds_half_up_to_the_cent(empty_db):
    cash_service.deposit(Decimal("10.005"))
    # $10.005 rounds up to $10.01
    assert cash_service.get_balance() == Decimal("10.01")

# Check that a zero deposit is refused and the balance stays unchanged.
def test_zero_deposit_is_refused_and_balance_unchanged(empty_db):
    with pytest.raises(InvalidAmountError):
        cash_service.deposit(Decimal(0))
    # Rejected deposit leaves the balance at $0.
    assert cash_service.get_balance() == Decimal(0)

# Check that a negative deposit is refused and the balance stays unchanged.
def test_negative_deposit_is_refused_and_balance_unchanged(empty_db):
    with pytest.raises(InvalidAmountError):
        cash_service.deposit(Decimal(-50))
    # Rejected deposit leaves the balance at $0.
    assert cash_service.get_balance() == Decimal(0)

# Check that a non-numeric deposit is refused.
def test_non_numeric_deposit_is_refused(empty_db):
    with pytest.raises(InvalidAmountError):
        cash_service.deposit("abc")
    # Invalid input leaves the balance at $0.
    assert cash_service.get_balance() == Decimal(0)