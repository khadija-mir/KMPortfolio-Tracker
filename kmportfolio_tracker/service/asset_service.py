import logging

from kmportfolio_tracker.models.asset import Asset
from kmportfolio_tracker.errors import (
    DuplicateAssetError,
    AssetNotFoundError,
    MissingReqInputError,
)

logger = logging.getLogger(__name__)
# like prof said, dont have DB rn, so need to store like this
assets = {}

#going to treat aapl == AAPL
def add_asset(ticker, name):
    ticker = ticker.strip().upper()
    name = name.strip()

    if not ticker or not name:
        raise MissingReqInputError("Ticker and asset name are required.")

    if ticker in assets:
        raise DuplicateAssetError(
            f"Asset '{ticker}' already exists."
        )

    asset = Asset(ticker, name)
    assets[ticker] = asset

    logger.info("Created asset %s", ticker)
    return asset

# KeyError = business error user can understand
def get_asset(ticker):
    ticker = ticker.strip().upper()

    try:
        return assets[ticker]
    except KeyError:
        raise AssetNotFoundError(
            f"No asset exists with ticker '{ticker}'."
        ) from None

def list_assets():
    return list(assets.values())