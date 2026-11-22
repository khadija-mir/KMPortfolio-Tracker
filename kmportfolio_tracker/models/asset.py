from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from kmportfolio_tracker.database import Base


class Asset(Base):
    __tablename__ = "assets"
    # Each asset gets its own database ID.
    id: Mapped[int] = mapped_column(primary_key=True)
    # Ticker should be unique
    ticker: Mapped[str] = mapped_column(String(10), unique=True)
    # Store the asset's name.
    name: Mapped[str] = mapped_column(String(100))

    def __str__(self):
        return f"[Ticker: {self.ticker} | Name: {self.name}]"
