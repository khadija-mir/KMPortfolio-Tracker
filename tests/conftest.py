from decimal import Decimal

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from kmportfolio_tracker import database
from kmportfolio_tracker.models import account, asset, portfolio, price, transaction  # noqa: F401
from kmportfolio_tracker.services import (
    asset_service,
    cash_service,
    portfolio_service,
)


#class inspo
#staticpool = every session shared connection to same in-memory db
@pytest.fixture
def empty_db(monkeypatch):
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
    )
    #SQLite supposedly ignores foreign key constraints by default, so we need to turn them on.
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection,record):
        connection.execute("PRAGMA foreign_keys=ON")
    database.Base.metadata.create_all(engine)
    # mock db
    monkeypatch.setattr(database, "get_engine", lambda: engine)
    yield engine
    engine.dispose()

#Create a portfolio w/ cash and asset for tests
@pytest.fixture
def funded_portfolio(empty_db):
    cash_service.deposit(Decimal(1000))
    asset_service.add_asset("AAPL", "Apple Inc.")
    portfolio_service.create_portfolio(
        "Growth",
        "Long-term growth",
    )
    portfolio_service.select_portfolio("Growth")
