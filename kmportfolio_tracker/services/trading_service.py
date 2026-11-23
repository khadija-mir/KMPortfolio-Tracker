import logging
from datetime import date

from kmportfolio_tracker import database
from kmportfolio_tracker.errors import (
    InsufficientSharesError,
    InvalidAmountError,
    InvalidQuantityError,
    PositionNotFoundError,
)
from kmportfolio_tracker.models.transaction import Transaction
from kmportfolio_tracker.services import (
    asset_service,
    cash_service,
    portfolio_service,
)
from kmportfolio_tracker.services.validation import (
    round_to_cents,
    round_to_four_places,
    to_decimal,
)
from kmportfolio_tracker.storage import transaction_store

logger = logging.getLogger(__name__)

# Buy shares and record the transaction in the database
def buy_asset(ticker, quantity, price):
    quantity = to_decimal(quantity, "Purchase quantity")
    price = to_decimal(price, "Purchase price")
    quantity = round_to_four_places(quantity)
    price = round_to_four_places(price)
    if quantity <= 0:
        raise InvalidQuantityError(
            "Purchase quantity must be greater than zero."
        )
    if price <= 0:
        raise InvalidAmountError(
            "Purchase price must be greater than zero."
        )
    #round the total cost before checking available cash
    #this is where I took out rounding function - deliberate bug. test failed and recorded in README.md
    total_cost = round_to_cents(quantity * price)
    with database.transaction() as session:
        asset = asset_service.get_asset(session, ticker)
        portfolio = portfolio_service.get_selected_portfolio(session)
        # The cash service handles the insufficient-funds rule
        cash_service.spend(session, total_cost)
        transaction = Transaction(
            portfolio=portfolio,
            asset=asset,
            side="buy",
            quantity=quantity,
            price_per_share=price,
            trade_date=date.today(),
        )
        transaction_store.add_transaction(session, transaction)

    logger.info(
        "Bought %s shares of %s at %s in %s",
        quantity, asset.ticker, price, portfolio.name,
    )

def sell_asset(ticker, quantity, price):
    quantity = to_decimal(quantity, "Sale quantity")
    price = to_decimal(price, "Sale price")
    quantity = round_to_four_places(quantity)
    price = round_to_four_places(price)
    if quantity <= 0:
        raise InvalidQuantityError(
            "Sale quantity must be greater than zero."
        )
    if price < 0:
        raise InvalidAmountError(
            "Sale price cannot be negative."
        )
    # Round the proceeds to cents before adding them to the balance
    proceeds = round_to_cents(quantity * price)
    with database.transaction() as session:
        asset = asset_service.get_asset(session, ticker)
        portfolio = portfolio_service.get_selected_portfolio(session)
        # Rebuild the current position from its saved transactions
        positions = portfolio_service.get_positions(session, portfolio)
        position = positions.get(asset.ticker)
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
        # Calculate realized gain before recording the sale
        realized_gain = position.sell(quantity, price)
        cash_service.receive(session, proceeds)
        transaction = Transaction(
            portfolio=portfolio,
            asset=asset,
            side="sell",
            quantity=quantity,
            price_per_share=price,
            trade_date=date.today(),
        )
        transaction_store.add_transaction(session, transaction)
        logger.info(
            "Sold %s shares of %s at %s in %s; realized gain %s",
            quantity,
            asset.ticker,
            price,
            portfolio.name,
            realized_gain,
        )