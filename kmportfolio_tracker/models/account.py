
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmportfolio_tracker.database import Base
from kmportfolio_tracker.models.portfolio import Portfolio


# Account represents the account table in the database.
class Account(Base):
    __tablename__ = "account"

    # The account gets its own database ID.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Store the account's cash balance with two decimal places.
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    # This can be empty because the user may not have selected a portfolio yet.
    # The foreign key points to the selected portfolio when one exists.
    selected_portfolio_id: Mapped[int | None] = mapped_column(
        ForeignKey("portfolios.id")
    )

    # This relationship gives us the selected portfolio object, or None if nothing is selected.
    selected_portfolio: Mapped[Portfolio | None] = relationship()
