from decimal import Decimal


class Position:
    def __init__(self, asset, quantity=Decimal("0"), average_cost=Decimal("0")):
        self.asset = asset
        self.quantity = quantity
        self.average_cost = average_cost

    def buy(self, quantity, price):
        total_cost = self.quantity * self.average_cost + quantity * price
        self.quantity += quantity
        self.average_cost = total_cost / self.quantity

    def sell(self, quantity, price):
        gain = (price - self.average_cost) * quantity
        self.quantity -= quantity
        return gain