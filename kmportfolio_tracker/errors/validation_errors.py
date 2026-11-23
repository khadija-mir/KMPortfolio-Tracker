from kmportfolio_tracker.errors.base_error import PortfolioTrackerError


class InvalidAmountError(PortfolioTrackerError):
    """Raised when a deposit or price is outside its allowed range."""

class MissingReqInputError(PortfolioTrackerError):
    """Raised when a required text field, such as a name, is blank."""