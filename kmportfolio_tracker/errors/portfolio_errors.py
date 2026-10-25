from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

# Raised when creating a portfolio whose name already exists. can't have same name, talked about in class
class DuplicatePortfolioError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

# Raised when no portfolio matches the given name.
class PortfolioNotFoundError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

# Raised when trading or viewing with no portfolio selected.
class NoPortfolioSelectedError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

# Raised when deleting a portfolio that still holds shares.
class PortfolioNotEmptyError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)