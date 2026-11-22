
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmportfolio_tracker.database import Base
from kmportfolio_tracker.models.asset import Asset


# Price represents the prices table in the database.
class Price(Base):
    __tablename__ = "prices"

    # Each price record gets its own database ID.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Each asset should have only one current price record.
    # unique=True prevents multiple current prices from being stored for the same asset.
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), unique=True)

    # Store the asset's current price with four decimal places.
    price: Mapped[Decimal] = mapped_column(Numeric(14, 4))

    # This relationship lets us access the asset associated with the price.
    asset: Mapped[Asset] = relationship(lazy="selectin")
