from decimal import Decimal

import pytest

from kmportfolio_tracker.errors import AssetNotFoundError, InvalidAmountError
from kmportfolio_tracker.services import asset_service, pricing_service


# Check that setting a new price replaces prev price.
def test_setting_a_price_again_replaces_the_old_one(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")
    pricing_service.set_price("AAPL", Decimal(150))
    pricing_service.set_price("AAPL", Decimal(200))
    asset, price = pricing_service.list_prices()[0]
    #AAPL should have a saved price of $200
    assert asset.ticker == "AAPL"
    assert price == Decimal(200)
    assert len(pricing_service.list_prices()) == 1

#Neg prices refused and prev price unchanged
def test_negative_price_is_refused_and_price_unchanged(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")
    pricing_service.set_price("AAPL", Decimal(150))
    with pytest.raises(InvalidAmountError):
        pricing_service.set_price("AAPL", Decimal(-1))
    asset, price = pricing_service.list_prices()[0]
    # The rejected update should leave AAPL at $150.
    assert asset.ticker == "AAPL"
    assert price == Decimal(150)

# zero price is allowed
def test_zero_price_is_allowed(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")
    pricing_service.set_price("AAPL", Decimal(0))
    asset, price = pricing_service.list_prices()[0]
    # AAPL should have a saved price of $0.
    assert asset.ticker == "AAPL"
    assert price == Decimal(0)

#setting a price for an unknown ticker is refused
def test_price_for_unknown_ticker_is_refused(empty_db):
    with pytest.raises(AssetNotFoundError):
        pricing_service.set_price("ZZZ", Decimal(10))
    # No price should be saved
    assert pricing_service.list_prices() == []
