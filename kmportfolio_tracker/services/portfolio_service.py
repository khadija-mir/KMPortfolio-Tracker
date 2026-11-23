import logging
from decimal import Decimal

from kmportfolio_tracker import database
from kmportfolio_tracker.errors import (
    DuplicatePortfolioError,
    MissingReqInputError,
    NoPortfolioSelectedError,
    PortfolioNotEmptyError,
    PortfolioNotFoundError,
)
from kmportfolio_tracker.models.portfolio import Portfolio
from kmportfolio_tracker.models.position import Position
from kmportfolio_tracker.models.report import HoldingRow, PortfolioReport
from kmportfolio_tracker.services import pricing_service
from kmportfolio_tracker.storage import (
    account_store,
    portfolio_store,
    transaction_store,
)

logger = logging.getLogger(__name__)

def create_portfolio(name, strategy):
    name = name.strip()
    strategy = strategy.strip()
    if not name or not strategy:
        raise MissingReqInputError(
            "Portfolio name and strategy description are required."
        )
    with database.transaction() as session:
        existing_portfolio = portfolio_store.get_portfolio(
            session, name
        )
        if existing_portfolio is not None:
            existing_name = existing_portfolio.name
            raise DuplicatePortfolioError(
                f"A portfolio named '{existing_name}' already exists."
                f" Select '{existing_name}' instead of creating a new one!"
            )
        portfolio = Portfolio(name=name, strategy=strategy)
        portfolio_store.add_portfolio(session, portfolio)
        logger.info("Created portfolio %s", name)
    return portfolio

# Return all portfolios and whether each one is currently selected
def list_portfolios():
    with database.transaction() as session:
        portfolios = portfolio_store.list_portfolios(session)
        selected_portfolio = account_store.get_selected_portfolio(session)
        return [(portfolio, selected_portfolio is not None and portfolio.id == selected_portfolio.id) for portfolio in portfolios]

# Find a portfolio by name
def get_portfolio(session, name):
    name = name.strip()
    portfolio = portfolio_store.get_portfolio(session, name)
    if portfolio is None:
        raise PortfolioNotFoundError(
            f"No portfolio named '{name}' exists."
        )
    return portfolio

# Select a portfolio for the account
def select_portfolio(name):
    with database.transaction() as session:
        portfolio = get_portfolio(session, name)
        account_store.set_selected_portfolio(session, portfolio)
        logger.info("Selected portfolio %s", portfolio.name)

# Return the selected portfolio or raise an error if none is selected
def get_selected_portfolio(session):
    portfolio = account_store.get_selected_portfolio(session)
    if portfolio is None:
        raise NoPortfolioSelectedError(
            "Select a portfolio first."
        )
    return portfolio

# Rebuild positions by replaying the portfolio's transactions
def get_positions(session, portfolio):
    positions = {}
    for trade in transaction_store.get_transactions(session, portfolio):
        ticker = trade.asset.ticker
        if ticker not in positions:
            positions[ticker] = Position(trade.asset)
        position = positions[ticker]
        if trade.side == "buy":
            position.buy(trade.quantity, trade.price_per_share)
        else:
            position.sell(trade.quantity, trade.price_per_share)
    # Keep fully sold positions because they may have realized gains
    return positions

# Delete a portfolio if it no longer holds any shares
def delete_portfolio(name):
    with database.transaction() as session:
        portfolio = get_portfolio(session, name)
        positions = get_positions(session, portfolio)
        for position in positions.values():
            if position.quantity > 0:
                raise PortfolioNotEmptyError(
                    "You should sell all shares before deleting this portfolio."
                )
        selected_portfolio = account_store.get_selected_portfolio(session)
        if (selected_portfolio is not None and selected_portfolio.id == portfolio.id):
            account_store.set_selected_portfolio(session, None)
        # Delete the trades before deleting the portfolio they reference
        transaction_store.delete_transactions(session, portfolio)
        portfolio_store.delete_portfolio(session, portfolio)
        logger.info("Deleted portfolio %s", name)

# Build a report for the currently selected portfolio.
def get_selected_portfolio_report():
    with database.transaction() as session:
        portfolio = get_selected_portfolio(session)
        positions = get_positions(session, portfolio)
        realized_gain_total = sum((position.realized_gain for position in positions.values()), Decimal(0))
        market_value_total = Decimal(0)
        unrealized_gain_total = Decimal(0)
        missing_prices = []
        holdings = []
        for position in positions.values():
            # Fully sold positions count toward realized gain, not current holdings.
            if position.quantity <= 0:
                continue
            ticker = position.asset.ticker
            current_price = pricing_service.get_price(session, ticker)
            if current_price is None:
                missing_prices.append(ticker)
            else:
                market_value_total += position.market_value(current_price)
                unrealized_gain_total += position.unrealized_gain(
                    current_price
                )
            holdings.append(HoldingRow(position, current_price))
        # Missing prices make the overall market value and unrealized gain incomplete.
        if missing_prices:
            market_value_total = None
            unrealized_gain_total = None
        return PortfolioReport(
            name=portfolio.name,
            strategy=portfolio.strategy,
            holdings=holdings,
            market_value_total=market_value_total,
            unrealized_gain_total=unrealized_gain_total,
            realized_gain_total=realized_gain_total,
            missing_prices=missing_prices,
        )