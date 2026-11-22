
import functools
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# This function creates the database engine --> SQLAlchemy communicate w/ the DB.
# It is a function instead of a module-level variable so tests can replace it with an in-memory database engine
@functools.cache
def get_engine():
    # Load the database settings from the .env file into the environment.
    load_dotenv()
    # URL.create builds the DB connection URL using env vars.
    url = URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),  # Port needs to be an integer.
        database=os.environ["DB_NAME"],
    )
    # Create the engine
    return create_engine(url)

class Base(DeclarativeBase):
    """Base class for all database models."""

def create_tables():
    Base.metadata.create_all(get_engine())

def transaction():
    # Create a session factory using the engine returned by get_engine().
    # expire_on_commit=False keeps objects readable after the session closes.
    Session = sessionmaker(get_engine(), expire_on_commit=False)
    # Session.begin() opens a transaction.
    # It automatically commits if everything succeeds and rolls back if an error occurs.
    return Session.begin()
