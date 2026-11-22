class Asset:
    def __init__(self, ticker, name):
        self.ticker = ticker
        self.name = name

    def __str__(self):
        return f"[Ticker: {self.ticker} | Name: {self.name}]"