from decimal import Decimal

import pytest

from kmportfolio_tracker.errors import (
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidAmountError,
    InvalidQuantityError,
    NoPortfolioSelectedError,
    PositionNotFoundError,
)
from kmportfolio_tracker.services import (
    asset_service,
    cash_service,
    portfolio_service,
    trading_service,
)


# Check that buying shares reduces cash by the purchase cost.
def test_buying_reduces_cash_by_the_cost(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(5), Decimal(100))
    # $1,000 - (5 x $100) = $500
    assert cash_service.get_balance() == Decimal("500.00")

# Check that purchase costs are rounded to the nearest cent.
def test_buy_cost_is_rounded_to_the_nearest_cent(empty_db):
    cash_service.deposit("100")
    asset_service.add_asset("AAPL", "Apple Inc.")
    portfolio_service.create_portfolio("Growth", "Long-term growth")
    portfolio_service.select_portfolio("Growth")
    trading_service.buy_asset("AAPL", Decimal(3), Decimal("33.3333"))
    # 3 x $33.3333 = $99.9999, rounded to $100.00
    assert cash_service.get_balance() == Decimal("0.00")

# Check that purchases exceeding available cash are refused.
def test_buy_costing_more_than_cash_is_refused_and_nothing_changes(funded_portfolio):
    with pytest.raises(InsufficientFundsError):
        trading_service.buy_asset("AAPL", Decimal(11), Decimal(100))
    # $1,000 - $1,100 would be negative, so the purchase is rejected.
    assert cash_service.get_balance() == Decimal("1000.00")
    assert portfolio_service.get_selected_portfolio_report().holdings == []

# Check that buying zero shares is refused.
def test_buying_zero_shares_is_refused(funded_portfolio):
    with pytest.raises(InvalidQuantityError):
        trading_service.buy_asset("AAPL", Decimal(0), Decimal(100))
    # Rejected purchase leaves the $1,000 balance unchanged.
    assert cash_service.get_balance() == Decimal("1000.00")

# Check that buying shares at zero price is refused.
def test_buying_at_zero_price_is_refused(funded_portfolio):
    with pytest.raises(InvalidAmountError):
        trading_service.buy_asset("AAPL", Decimal(5), Decimal(0))
    # Rejected purchase leaves the $1,000 balance unchanged.
    assert cash_service.get_balance() == Decimal("1000.00")

# Check that selling shares adds the sale proceeds to cash.
def test_selling_adds_proceeds_to_cash(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(10), Decimal(100))
    trading_service.sell_asset("AAPL", Decimal(4), Decimal(130))
    # $0 + (4 x $130) = $520
    assert cash_service.get_balance() == Decimal("520.00")

# Check that selling shares at zero price is allowed.
def test_selling_at_zero_price_is_allowed(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(10), Decimal(100))
    trading_service.sell_asset("AAPL", Decimal(10), Decimal(0))
    report = portfolio_service.get_selected_portfolio_report()
    # (10 x $100) purchase cost, with $0 sale proceeds.
    assert cash_service.get_balance() == Decimal("0.00")
    # ($0 sale price - $100 average cost) x 10 shares = -$1,000
    assert report.realized_gain_total == Decimal(-1000)

# Check that selling more shares than held is refused.
def test_selling_more_than_held_is_refused_and_nothing_changes(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(5), Decimal(100))
    with pytest.raises(InsufficientSharesError):
        trading_service.sell_asset("AAPL", Decimal(6), Decimal(100))
    # $1,000 - (5 x $100) = $500
    assert cash_service.get_balance() == Decimal("500.00")
    holdings = portfolio_service.get_selected_portfolio_report().holdings
    assert holdings[0].quantity == Decimal(5)

# Check that selling an asset with no shares held is refused.
def test_selling_an_unheld_asset_is_refused(funded_portfolio):
    with pytest.raises(PositionNotFoundError):
        trading_service.sell_asset("AAPL", Decimal(1), Decimal(100))
    # Rejected sale leaves the $1,000 balance unchanged.
    assert cash_service.get_balance() == Decimal("1000.00")

# Check that buying shares without a selected portfolio is refused.
def test_buying_without_a_selected_portfolio_is_refused(empty_db):
    cash_service.deposit("1000")
    asset_service.add_asset("AAPL", "Apple Inc.")
    portfolio_service.create_portfolio("Growth", "Long-term growth")
    with pytest.raises(NoPortfolioSelectedError):
        trading_service.buy_asset("AAPL", Decimal(1), Decimal(100))
    # Rejected purchase leaves the $1,000 balance unchanged.
    assert cash_service.get_balance() == Decimal("1000.00")

# Check that buying is allowed when the rounded cost equals available cash.
def test_buy_is_allowed_when_rounded_cost_equals_cash(empty_db):
    cash_service.deposit("100")
    asset_service.add_asset("AAPL", "Apple Inc.")
    portfolio_service.create_portfolio("Growth", "Long-term growth")
    portfolio_service.select_portfolio("Growth")
    trading_service.buy_asset("AAPL", Decimal(3), Decimal("33.3334"))
    # 3 x $33.3334 = $100.0002, rounded to $100.00
    assert cash_service.get_balance() == Decimal("0.00")