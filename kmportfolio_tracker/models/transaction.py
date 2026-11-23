from datetime import date
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmportfolio_tracker.database import Base
from kmportfolio_tracker.models.asset import Asset
from kmportfolio_tracker.models.portfolio import Portfolio


# Transaction table
class Transaction(Base):
    __tablename__ = "transactions"
    # DB ID for others to reference
    id: Mapped[int] = mapped_column(primary_key=True)
    # FK connectors to portfolios and assets
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    # Only allow a transaction to be a buy or a sell
    side: Mapped[str] = mapped_column(Enum("buy", "sell"))
    # Store the quantity and price with four decimal places
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    price_per_share: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    # Store the date the trade took place
    trade_date: Mapped[date]
    # These relationships let us access the actual portfolio and asset objects
    portfolio: Mapped[Portfolio] = relationship()
    # Load the related asset along with the transactions
    # This way, we can still access the asset after the database session closes
    # It also avoids sending a separate query for every asset when processing trades
    asset: Mapped[Asset] = relationship(lazy="selectin")
