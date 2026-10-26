from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

#Raised when a deposit or price is outside its allowed range.
class InvalidAmountError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

#Raised when a required text field, such as a name, is blank.
class MissingReqInputError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)