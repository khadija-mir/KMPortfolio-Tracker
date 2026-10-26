import logging
from decimal import Decimal

from kmportfolio_tracker.service import pricing_service
from kmportfolio_tracker.models.portfolio import Portfolio
from kmportfolio_tracker.errors import (
    DuplicatePortfolioError,
    PortfolioNotFoundError,
    NoPortfolioSelectedError,
    PortfolioNotEmptyError,
    MissingReqInputError,
)

logger = logging.getLogger(__name__)

portfolios = {}
selected_portfolio = None

def create_portfolio(name, description):
    name = name.strip()
    description = description.strip()
    if not name or not description:
        raise MissingReqInputError(
            "Portfolio name and strategy description are required."
        )
    #ignore case, so "Tech" == "tech" (same portfolio)
    lowercase_name = name.lower()
    if lowercase_name in portfolios:
        existing_name = portfolios[lowercase_name].name
        raise DuplicatePortfolioError(
            f"A portfolio named '{existing_name}' already exists."
            f" Select '{existing_name}' instead of creating a new one!"
        )
    portfolios[lowercase_name] = Portfolio(name, description)
    logger.info("Created portfolio %s", name)
    return portfolios[lowercase_name]

def list_portfolios():
    return [
        (portfolio, portfolio is selected_portfolio)
        for portfolio in portfolios.values()
    ]

def get_portfolio(name):
    name = name.strip()
    try:
        return portfolios[name.lower()]
    except KeyError:
        raise PortfolioNotFoundError(
            f"No portfolio named '{name}' exists."
        )
    
def select_portfolio(name):
    global selected_portfolio
    selected_portfolio = get_portfolio(name)
    logger.info("Selected portfolio %s", name)

def get_selected_portfolio():
    if selected_portfolio is None:
        raise NoPortfolioSelectedError(
            "Select a portfolio before trading."
        )
    return selected_portfolio

def delete_portfolio(name):
    global selected_portfolio

    portfolio = get_portfolio(name)

    if any(p.quantity > 0 for p in portfolio.positions.values()):
        raise PortfolioNotEmptyError(
            "You should sell all shares before deleting this portfolio."
        )

    del portfolios[portfolio.name.lower()]
    if selected_portfolio is portfolio:
        selected_portfolio = None
    logger.info("Deleted portfolio %s", name)

def get_selected_portfolio_report():
    portfolio = get_selected_portfolio()
    positions = []
    market_value_total = Decimal("0")
    unrealized_gain_total = Decimal("0")
    missing_prices = []
    for position in portfolio.positions.values():
        # Fully sold positions are intentionally hidden.
        if position.quantity <= 0:
            continue
        current_price = pricing_service.get_price(
            position.asset.ticker
        )
        if current_price is None:
            missing_prices.append(position.asset.ticker)
            positions.append({
                "ticker": position.asset.ticker,
                "name": position.asset.name,
                "quantity": position.quantity,
                "average_cost": position.average_cost,
                "current_price": None,
                "market_value": None,
                "unrealized_gain": None,
            })
            continue
        market_value = position.quantity * current_price
        unrealized_gain = (
            current_price - position.average_cost
        ) * position.quantity
        market_value_total += market_value
        unrealized_gain_total += unrealized_gain
        positions.append({
            "ticker": position.asset.ticker,
            "name": position.asset.name,
            "quantity": position.quantity,
            "average_cost": position.average_cost,
            "current_price": current_price,
            "market_value": market_value,
            "unrealized_gain": unrealized_gain,
        })
    # If a price is missing, the total would be wrong, so don't show one.
    if missing_prices:
        market_value_total = None
        unrealized_gain_total = None

    return {
        "name": portfolio.name,
        "description": portfolio.description,
        "positions": positions,
        "market_value_total": market_value_total,
        "unrealized_gain_total": unrealized_gain_total,
        "realized_gain_total": portfolio.realized_gain,
        "missing_prices": missing_prices,
    }