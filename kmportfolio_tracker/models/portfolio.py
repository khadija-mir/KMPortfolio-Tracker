from decimal import Decimal


class Portfolio:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.positions = {}
        self.trade_history = []
        self.realized_gain = Decimal("0")

    def __str__(self):
        return (
            f"[Portfolio: {self.name} | "
            f"Strategy: {self.description}]"
        )