from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

# Raised when a buy or sell quantity is not greater than zero.
class InvalidQuantityError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

# Raised when selling an asset the portfolio does not hold.
class PositionNotFoundError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

# Raised when selling more shares than the portfolio holds.
class InsufficientSharesError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)