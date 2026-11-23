from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from kmportfolio_tracker.database import Base


# Portfolio table
class Portfolio(Base):
    __tablename__ = "portfolios"
    # Each portfolio gets its own database ID.
    #stable reference for tables
    id: Mapped[int] = mapped_column(primary_key=True)
    # Portfolio names must be unique.
    name: Mapped[str] = mapped_column(String(100), unique=True)
    # Store the portfolio's investment strategy.
    strategy: Mapped[str] = mapped_column(String(255))
    def __str__(self):
        return (
            f"[Portfolio: {self.name} | "
            f"Strategy: {self.strategy}]"
        )