import logging

from kmportfolio_tracker import database
from kmportfolio_tracker.errors import (
    InsufficientFundsError,
    InvalidAmountError,
)
from kmportfolio_tracker.services.validation import (
    round_to_cents,
    to_decimal,
)
from kmportfolio_tracker.storage import account_store

logger = logging.getLogger(__name__)


# Deposit money into the account.
def deposit(amount):
    amount = to_decimal(amount, "Deposit amount")
    amount = round_to_cents(amount)

    if amount <= 0:
        raise InvalidAmountError(
            "Deposit amount must be greater than zero."
        )

    # The account balance is shared across all portfolios.
    with database.transaction() as session:
        balance = account_store.get_cash_balance(session)
        account_store.set_cash_balance(session, balance + amount)

        logger.info(
            "Deposited %s; balance is %s",
            amount,
            balance + amount,
        )


# Return the current account cash balance.
def get_balance():
    with database.transaction() as session:
        return account_store.get_cash_balance(session)


# Spend cash from the account.
# This helper uses the transaction opened by the calling service.
def spend(session, amount):
    balance = account_store.get_cash_balance(session)

    if amount > balance:
        raise InsufficientFundsError(
            f"Insufficient funds. Available cash: ${balance}; "
            f"amount needed: ${amount}."
        )

    account_store.set_cash_balance(session, balance - amount)


# Add money to the account.
# This helper uses the transaction opened by the calling service.
def receive(session, amount):
    balance = account_store.get_cash_balance(session)
    account_store.set_cash_balance(session, balance + amount)
