from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

# Raised when a purchase costs more than the cash balance.
class InsufficientFundsError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)