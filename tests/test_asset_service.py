import pytest

from kmportfolio_tracker.errors import (
    DuplicateAssetError,
    MissingReqInputError,
)
from kmportfolio_tracker.services import asset_service


# want consistent ticker format
def test_ticker_is_stored_in_uppercase(empty_db):
    asset_service.add_asset("aapl", "Apple Inc.")
    assets = asset_service.list_assets()
    assert assets[0].ticker == "AAPL"

# Check that duplicate tickers are refused regardless of case
def test_duplicate_ticker_in_any_case_is_refused(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")
    with pytest.raises(DuplicateAssetError):
        asset_service.add_asset("aapl", "Apple again")
    # The duplicate should not create another asset
    assert len(asset_service.list_assets()) == 1

# Check that blank tickers are refused
def test_blank_ticker_is_refused(empty_db):
    with pytest.raises(MissingReqInputError):
        asset_service.add_asset("   ", "Apple Inc.")
    # No asset should be added when the ticker is blank
    assert asset_service.list_assets() == []
    
# Check that assets cannot be added without a name
def test_blank_asset_name_is_refused(empty_db):
    with pytest.raises(MissingReqInputError):
        asset_service.add_asset("AAPL", "   ")
    assert asset_service.list_assets() == []