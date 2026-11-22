from sqlalchemy import func, select

from kmportfolio_tracker.models.portfolio import Portfolio


# Add a portfolio
def add_portfolio(session, portfolio):
    session.add(portfolio)

#get portfolio by name, case insensitive
def get_portfolio(session, name):
    return session.scalars(
        select(Portfolio).where(
            func.lower(Portfolio.name) == name.lower()
        )
    ).first()

# Return all portfolios, ordered alphabetically by name.
def list_portfolios(session):
    return session.scalars(
        select(Portfolio).order_by(Portfolio.name)
    ).all()

# Delete a portfolio
def delete_portfolio(session, portfolio):
    session.delete(portfolio)
