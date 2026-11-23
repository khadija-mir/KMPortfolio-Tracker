from decimal import Decimal

from sqlalchemy import select

from kmportfolio_tracker.models.account import Account


# Get acct, create if neccessary
def get_account(session):
    account = session.scalars(select(Account)).first()
    if account is None:
        account = Account(cash_balance=Decimal(0))
        session.add(account)
    return account

# Get the current cash balance from the account.
def get_cash_balance(session):
    account = get_account(session)
    return account.cash_balance

# Update the account's cash balance.
def set_cash_balance(session, amount):
    account = get_account(session)
    account.cash_balance = amount

# Return the portfolio currently selected for the account.
def get_selected_portfolio(session):
    account = get_account(session)
    return account.selected_portfolio


# Set the account's selected portfolio.
# Passing None clears the selection.
def set_selected_portfolio(session, portfolio):
    account = get_account(session)
    account.selected_portfolio = portfolio
