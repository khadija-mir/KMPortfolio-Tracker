from sqlalchemy import select

from kmportfolio_tracker.models.transaction import Transaction


# Add transaction to db
def add_transaction(session, transaction):
    session.add(transaction)

# Return all transactions for a portfolio, in the order they happened
def get_transactions(session, portfolio):
    return session.scalars(
        select(Transaction)
        .filter_by(portfolio_id=portfolio.id)
        .order_by(Transaction.id)
    ).all()

# Delete all transactions belonging to a portfolio
def delete_transactions(session, portfolio):
    for transaction in get_transactions(session, portfolio):
        session.delete(transaction)