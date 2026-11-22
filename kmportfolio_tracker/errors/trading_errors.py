from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

class InvalidQuantityError(PortfolioTrackerError):
    """Raised when a buy or sell quantity is not greater than zero."""

class PositionNotFoundError(PortfolioTrackerError):
    """Raised when selling an asset the portfolio does not hold."""

class InsufficientSharesError(PortfolioTrackerError):
    """Raised when selling more shares than the portfolio holds."""