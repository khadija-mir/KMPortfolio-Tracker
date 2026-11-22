import logging
from decimal import Decimal

from kmportfolio_tracker.errors import (
    InvalidAmountError,
    InsufficientFundsError,
)

logger = logging.getLogger(__name__)
#"One cash balance is shared by all portfolios" - calc rules
cash_balance = Decimal("0")

def deposit(amount):
    global cash_balance
    amount = Decimal(amount)
    if amount <= 0:
        raise InvalidAmountError(
            "Deposit amount must be greater than zero."
        )
    cash_balance += amount
    logger.info("Deposited %s; balance is %s", amount, cash_balance)

def get_balance():
    return cash_balance

def spend(amount):
    global cash_balance
    amount = Decimal(amount)
    #cash != negative
    if amount > cash_balance:
        raise InsufficientFundsError(
            f"Insufficient funds. Available cash: ${cash_balance}."
        )
    cash_balance -= amount

def receive(amount):
    global cash_balance
    cash_balance += Decimal(amount)