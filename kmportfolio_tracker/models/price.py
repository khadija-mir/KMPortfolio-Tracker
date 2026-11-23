from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmportfolio_tracker.database import Base
from kmportfolio_tracker.models.asset import Asset


# Price table
class Price(Base):
    __tablename__ = "prices"
    # DB ID for others to reference
    id: Mapped[int] = mapped_column(primary_key=True)
    # Each asset = only one current price record
    # unique=True prevents multiple current prices
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), unique=True)
    # asset's current price with four decimal places
    price: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    # This relationship lets us access the asset associated with the price/shown in class
    asset: Mapped[Asset] = relationship(lazy="selectin")
