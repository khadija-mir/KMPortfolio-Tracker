from kmportfolio_tracker.errors.base_error import PortfolioTrackerError

class DuplicateAssetError(PortfolioTrackerError):
    """Error when adding an asset whose ticker already exists."""
    
class AssetNotFoundError(PortfolioTrackerError):
    """Raised when no asset matches the given ticker."""