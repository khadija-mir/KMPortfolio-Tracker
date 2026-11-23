from decimal import Decimal

import pytest

from kmportfolio_tracker.errors import (
    DuplicatePortfolioError,
    MissingReqInputError,
    NoPortfolioSelectedError,
    PortfolioNotEmptyError,
    PortfolioNotFoundError,
    PositionNotFoundError,
)
from kmportfolio_tracker.services import (
    cash_service,
    portfolio_service,
    pricing_service,
    trading_service,
)


#refuse dupes in diff cases
def test_duplicate_portfolio_name_in_different_case_is_refused(funded_portfolio):
    with pytest.raises(DuplicatePortfolioError):
        portfolio_service.create_portfolio("GROWTH", "x")
    # The original Growth portfolio should be the only one.
    assert len(portfolio_service.list_portfolios()) == 1

# Check that portfolio reports calculate market value and unrealized gain
def test_report_values_holdings_at_the_current_price(funded_portfolio, monkeypatch):
    monkeypatch.setattr(
        pricing_service,
        "get_price",
        lambda session, ticker: Decimal(150),
    )
    trading_service.buy_asset("AAPL", Decimal(10), Decimal(100))
    report = portfolio_service.get_selected_portfolio_report()
    # 10 shares x $150 = $1,500
    assert report.market_value_total == Decimal(1500)
    # ($150 current price - $100 average cost) x 10 = $500
    assert report.unrealized_gain_total == Decimal(500)

# Check that report totals are unavailable when a price is missing
def test_report_totals_are_unavailable_when_a_price_is_missing(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(10), Decimal(100))
    report = portfolio_service.get_selected_portfolio_report()
    assert report.market_value_total is None
    assert report.missing_prices == ["AAPL"]

# Check that realized gain includes positions that are fully sold
def test_realized_gain_counts_fully_sold_positions(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(10), Decimal(100))
    trading_service.sell_asset("AAPL", Decimal(10), Decimal(120))
    report = portfolio_service.get_selected_portfolio_report()
    # ($120 sale price - $100 average cost) x 10 = $200
    assert report.realized_gain_total == Decimal(200)
    assert report.holdings == []

# Check that portfolios with shares held cannot be deleted
def test_portfolio_holding_shares_cannot_be_deleted(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(1), Decimal(100))
    with pytest.raises(PortfolioNotEmptyError):
        portfolio_service.delete_portfolio("Growth")
    # portfolio should still exist after the rejected deletion
    assert len(portfolio_service.list_portfolios()) == 1

# Check that deleting a portfolio clears the selected portfolio
def test_deleting_a_portfolio_clears_the_selection(funded_portfolio):
    portfolio_service.delete_portfolio("Growth")
    assert portfolio_service.list_portfolios() == []
    with pytest.raises(NoPortfolioSelectedError):
        portfolio_service.get_selected_portfolio_report()

# Check that selecting an unknown portfolio is refused without changing selection
def test_selecting_an_unknown_portfolio_is_refused(funded_portfolio):
    with pytest.raises(PortfolioNotFoundError):
        portfolio_service.select_portfolio("Income")
    report = portfolio_service.get_selected_portfolio_report()
    assert report.name == "Growth"

# Check that portfolio selection ignores differences in capitalization
def test_selecting_a_portfolio_ignores_case(funded_portfolio):
    portfolio_service.select_portfolio("growth")
    report = portfolio_service.get_selected_portfolio_report()
    assert report.name == "Growth"

# Check that portfolios cannot be created with blank
def test_blank_portfolio_name_is_refused(empty_db):
    with pytest.raises(MissingReqInputError):
        portfolio_service.create_portfolio("   ", "Long-term growth")
    assert portfolio_service.list_portfolios() == []

# check refusal of blank strategy
def test_blank_portfolio_strategy_is_refused(empty_db):
    with pytest.raises(MissingReqInputError):
        portfolio_service.create_portfolio("Growth", "   ")
    assert portfolio_service.list_portfolios() == []

# Check that you can only sell positions that in your selected portfolio
def test_positions_are_kept_separate_per_portfolio(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(5), Decimal(100))
    portfolio_service.create_portfolio("Income", "Dividends")
    portfolio_service.select_portfolio("Income")
    with pytest.raises(PositionNotFoundError):
        trading_service.sell_asset("AAPL", Decimal(1), Decimal(100))
    # Rejected sale leaves the $500 cash balance unchanged
    assert cash_service.get_balance() == Decimal("500.00")
    assert portfolio_service.get_selected_portfolio_report().holdings == []
    portfolio_service.select_portfolio("Growth")
    # Growth should still have all 5 shares
    assert portfolio_service.get_selected_portfolio_report().holdings[0].quantity == Decimal(5)

# Check that a portfolio can be deleted after all shares are sold
def test_deleting_a_fully_sold_portfolio_is_allowed(funded_portfolio):
    trading_service.buy_asset("AAPL", Decimal(5), Decimal(100))
    trading_service.sell_asset("AAPL", Decimal(5), Decimal(100))
    portfolio_service.delete_portfolio("Growth")
    assert portfolio_service.list_portfolios() == []

# Check that deleting an unknown portfolio is refused
def test_deleting_an_unknown_portfolio_is_refused(funded_portfolio):
    with pytest.raises(PortfolioNotFoundError):
        portfolio_service.delete_portfolio("Income")
    assert len(portfolio_service.list_portfolios()) == 1
