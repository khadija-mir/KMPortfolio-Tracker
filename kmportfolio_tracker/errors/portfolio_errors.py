from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

class DuplicatePortfolioError(PortfolioTrackerError):
    """Raised when creating a portfolio whose name already exists."""

class PortfolioNotFoundError(PortfolioTrackerError):
    """Raised when no portfolio matches the given name."""

class NoPortfolioSelectedError(PortfolioTrackerError):
    """Raised when trading or viewing without selecting a portfolio."""

class PortfolioNotEmptyError(PortfolioTrackerError):
    """Raised when deleting a portfolio that still holds shares."""