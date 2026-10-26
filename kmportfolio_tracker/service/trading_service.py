import logging
from decimal import Decimal

from kmportfolio_tracker.service import (
    asset_service,
    portfolio_service,
    cash_service,
)
from kmportfolio_tracker.models.position import Position
from kmportfolio_tracker.errors import (
    InvalidAmountError,
    InvalidQuantityError,
    InsufficientFundsError,
    PositionNotFoundError,
    InsufficientSharesError,
)

logger = logging.getLogger(__name__)


def buy_asset(ticker, quantity, price):
    asset = asset_service.get_asset(ticker)
    portfolio = portfolio_service.get_selected_portfolio()

    quantity = Decimal(quantity)
    price = Decimal(price)

    if quantity <= 0:
        raise InvalidQuantityError(
            "Purchase quantity must be greater than zero."
        )

    if price <= 0:
        raise InvalidAmountError(
            "Purchase price must be greater than zero."
        )

    total_cost = quantity * price

    # Validate available cash before changing the position.
    if total_cost > cash_service.get_balance():
        raise InsufficientFundsError(
            f"Purchase costs ${total_cost}, but only "
            f"${cash_service.get_balance()} is available."
        )

    position = portfolio.positions.get(asset.ticker)

    if position is None:
        position = Position(asset)
        portfolio.positions[asset.ticker] = position

    cash_service.spend(total_cost)
    position.buy(quantity, price)

    portfolio.trade_history.append({
        "type": "BUY",
        "ticker": asset.ticker,
        "quantity": quantity,
        "price": price,
        "total": total_cost,
    })

    logger.info(
        "Bought %s shares of %s at %s in %s",
        quantity, asset.ticker, price, portfolio.name,
    )


def sell_asset(ticker, quantity, price):
    asset = asset_service.get_asset(ticker)
    portfolio = portfolio_service.get_selected_portfolio()

    quantity = Decimal(quantity)
    price = Decimal(price)

    if quantity <= 0:
        raise InvalidQuantityError(
            "Sale quantity must be greater than zero."
        )

    if price < 0:
        raise InvalidAmountError(
            "Sale price cannot be negative."
        )

    position = portfolio.positions.get(asset.ticker)

    if position is None or position.quantity <= 0:
        raise PositionNotFoundError(
            f"No shares of '{asset.ticker}' are held in "
            f"'{portfolio.name}'."
        )

    if quantity > position.quantity:
        raise InsufficientSharesError(
            f"You hold {position.quantity} shares, "
            f"so you cannot sell {quantity}."
        )

    proceeds = quantity * price
    realized_gain = position.sell(quantity, price)

    cash_service.receive(proceeds)
    portfolio.realized_gain += realized_gain

    portfolio.trade_history.append({
        "type": "SELL",
        "ticker": asset.ticker,
        "quantity": quantity,
        "price": price,
        "total": proceeds,
        "realized_gain": realized_gain,
    })

    logger.info(
        "Sold %s shares of %s at %s in %s; realized gain %s",
        quantity, asset.ticker, price,
        portfolio.name, realized_gain,
    )