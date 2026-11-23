from decimal import Decimal


#Position table
class Position:
    def __init__(self, asset, quantity=Decimal(0), average_cost=Decimal(0)):
        self.asset = asset
        self.quantity = quantity
        self.average_cost = average_cost
        self.realized_gain = Decimal(0)

    def buy(self, quantity, price):
        total_cost = self.quantity * self.average_cost + quantity * price
        self.quantity += quantity
        self.average_cost = total_cost / self.quantity

    def sell(self, quantity, price):
        gain = (price - self.average_cost) * quantity
        self.quantity -= quantity
        self.realized_gain += gain
        return gain
    
    def market_value(self, price):
        return self.quantity * price
    def unrealized_gain(self, price):
        return (price - self.average_cost) * self.quantity