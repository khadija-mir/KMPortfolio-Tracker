
from sqlalchemy import select

from kmportfolio_tracker.models.asset import Asset


#add asset to database
def add_asset(session, asset):
    session.add(asset)

# use ticker to find asset
def get_asset(session, ticker):
    return session.scalars(
        select(Asset).filter_by(ticker=ticker)
    ).first()

#list assets
def list_assets(session):
    return session.scalars(
        select(Asset).order_by(Asset.ticker)
    ).all()
