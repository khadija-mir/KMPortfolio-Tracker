from sqlalchemy import select

from kmportfolio_tracker.models.price import Price


# Find price row for asset
def _find_price_row(session, asset):
    return session.scalars(
        select(Price).filter_by(asset_id=asset.id)
    ).first()

# get the current price for an asset/return None if not set
def get_price(session, asset):
    price_row = _find_price_row(session, asset)
    if price_row is None:
        return None
    return price_row.price

# set price
def set_price(session, asset, price):
    price_row = _find_price_row(session, asset)
    if price_row is not None:
        price_row.price = price
    else:
        session.add(Price(asset=asset, price=price))
