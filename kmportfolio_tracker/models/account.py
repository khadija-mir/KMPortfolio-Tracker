from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmportfolio_tracker.database import Base
from kmportfolio_tracker.models.portfolio import Portfolio


# Account table
class Account(Base):
    __tablename__ = "account"
    #DB id for others to also reference
    id: Mapped[int] = mapped_column(primary_key=True)
    #store cash balance in account, 14 digits, 2 decimal places
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    #The foreign key points to the selected portfolio when one exists.
    selected_portfolio_id: Mapped[int | None] = mapped_column(
        ForeignKey("portfolios.id")
    )
    # This relationship gives us the selected portfolio object / None if nothing  selected
    selected_portfolio: Mapped[Portfolio | None] = relationship()
