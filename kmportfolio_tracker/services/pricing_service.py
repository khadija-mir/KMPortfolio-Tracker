import logging

from kmportfolio_tracker import database
from kmportfolio_tracker.errors import InvalidAmountError
from kmportfolio_tracker.services import asset_service
from kmportfolio_tracker.services.validation import (
    round_to_four_places,
    to_decimal,
)
from kmportfolio_tracker.storage import asset_store, price_store

logger = logging.getLogger(__name__)
# Set the current price for an asset and save it in the database
def set_price(ticker, price):
    price = to_decimal(price, "Current price")
    price = round_to_four_places(price)
    if price < 0:
        raise InvalidAmountError("Price cannot be negative.")
    with database.transaction() as session:
        asset = asset_service.get_asset(session, ticker)
        price_store.set_price(session, asset, price)
        logger.info("Updated current price for %s to %s", asset.ticker, price)

# Retrieve the current price for an asset
def get_price(session, ticker):
    asset = asset_service.get_asset(session, ticker)
    return price_store.get_price(session, asset)

#Return all assets with their current prices
def list_prices():
    with database.transaction() as session:
        assets = asset_store.list_assets(session)
        return [(asset, price_store.get_price(session, asset)) for asset in assets]