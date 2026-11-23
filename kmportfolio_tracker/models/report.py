
class HoldingRow:
    def __init__(self, position, price):
        self.ticker = position.asset.ticker
        self.name = position.asset.name
        self.quantity = position.quantity
        self.average_cost = position.average_cost
        self.current_price = price

        # A missing price means we cannot calculate the market value or gain.
        if price is None:
            self.market_value = None
            self.unrealized_gain = None
        else:
            self.market_value = position.market_value(price)
            self.unrealized_gain = position.unrealized_gain(price)


class PortfolioReport:
    def __init__(
        self,
        name,
        strategy,
        holdings,
        market_value_total,
        unrealized_gain_total,
        realized_gain_total,
        missing_prices,
    ):
        self.name = name
        self.strategy = strategy
        self.holdings = holdings
        self.market_value_total = market_value_total
        self.unrealized_gain_total = unrealized_gain_total
        self.realized_gain_total = realized_gain_total
        self.missing_prices = missing_prices
