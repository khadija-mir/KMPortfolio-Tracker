from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

#Error when adding an asset whose ticker already exists.
class DuplicateAssetError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)

# Raised when no asset matches the given ticker.
class AssetNotFoundError(PortfolioTrackerError):
    def __init__(self, message):
        super().__init__(message)