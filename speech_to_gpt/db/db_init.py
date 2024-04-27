from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine("sqlite:///./users.db")
if not database_exists(engine.url):
    create_database(engine.url)


def get_session_maker() -> sessionmaker:
    session = sessionmaker(bind=engine)
    return session
