from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from darts import settings


Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
session_factory = sessionmaker(bind=engine)

# Don't use this during web requests
Session = scoped_session(session_factory)
