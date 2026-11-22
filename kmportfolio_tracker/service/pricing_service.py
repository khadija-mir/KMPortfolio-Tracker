import logging
from decimal import Decimal

from kmportfolio_tracker.service import asset_service
from kmportfolio_tracker.errors import InvalidAmountError

logger = logging.getLogger(__name__)

current_prices = {}

def set_price(ticker, price):
    asset = asset_service.get_asset(ticker)
    # talked about using Decimal in class
    price = Decimal(price)

    if price < 0:
        raise InvalidAmountError("Current price cannot be negative.")

    current_prices[asset.ticker] = price
    logger.info("Set price for %s to %s", asset.ticker, price)


def get_price(ticker):
    return current_prices.get(ticker.strip().upper())