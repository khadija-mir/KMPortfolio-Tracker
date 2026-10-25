# Base class for every error raised by the portfolio tracker.
class PortfolioTrackerError(Exception):
    def __init__(self, message):
        super().__init__(message)