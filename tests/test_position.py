from decimal import Decimal

from kmportfolio_tracker.models.position import Position


# Check that multiple purchases update the avg cost
def test_buying_twice_averages_the_cost():
    position = Position(None)
    position.buy(Decimal(10), Decimal(100))
    position.buy(Decimal(10), Decimal(120))
    # (10 x $100 + 10 x $120) / 20 shares = $110
    assert position.average_cost == Decimal(110)

# Check that selling shares calculates the gain using avg cost
def test_selling_returns_gain_against_average_cost():
    position = Position(None)
    position.buy(Decimal(10), Decimal(100))
    gain = position.sell(Decimal(4), Decimal(130))
    # ($130 - $100 avg cost) x 4 shares = $120
    assert gain == Decimal(120)

# Check that selling shares does not change avg cost
def test_selling_does_not_change_average_cost():
    position = Position(None)
    position.buy(Decimal(10), Decimal(100))
    position.sell(Decimal(4), Decimal(130))
    # Selling changes quantity only, so avg cost stays $100
    assert position.average_cost == Decimal(100)

# Check that a lower mkt price results in a negative unrealized gain
def test_unrealized_gain_is_negative_when_price_falls():
    position = Position(None)
    position.buy(Decimal(10), Decimal(100))
    gain = position.unrealized_gain(Decimal(90))
    # ($90 - $100) x 10 shares = -$100
    assert gain == Decimal(-100)

# Check that mkt value uses the current price
def test_market_value_is_quantity_times_price():
    position = Position(None)
    position.buy(Decimal(10), Decimal(100))
    market_value = position.market_value(Decimal(150))
    # 10 shares x $150 = $1,500
    assert market_value == Decimal(1500)