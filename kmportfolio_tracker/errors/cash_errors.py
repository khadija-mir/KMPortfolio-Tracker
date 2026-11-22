from kmportfolio_tracker.errors.base_error import PortfolioTrackerError


class InsufficientFundsError(PortfolioTrackerError):
    """Raised when a purchase exceeds the cash balance."""