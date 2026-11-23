import logging

from kmportfolio_tracker import database
from kmportfolio_tracker.errors import (
    AssetNotFoundError,
    DuplicateAssetError,
    MissingReqInputError,
)
from kmportfolio_tracker.models.asset import Asset
from kmportfolio_tracker.storage import asset_store

logger = logging.getLogger(__name__)

# add asset
def add_asset(ticker, name):
    ticker = ticker.strip().upper()
    name = name.strip()

    if not ticker or not name:
        raise MissingReqInputError("Ticker and asset name are required.")

    with database.transaction() as session:
        if asset_store.get_asset(session, ticker) is not None:
            raise DuplicateAssetError(
            f"Asset '{ticker}' already exists."
        )

        asset = Asset(ticker = ticker, name = name)
        asset_store.add_asset(session, asset)

        logger.info("Created asset %s", ticker)
    return asset

def get_asset(session,ticker):
    ticker = ticker.strip().upper()
    asset = asset_store.get_asset(session, ticker)
    if asset is None:
        raise AssetNotFoundError(
            f"No asset exists with ticker '{ticker}'."
        )
    return asset

def list_assets():
    with database.transaction() as session:
        return asset_store.list_assets(session)