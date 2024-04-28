from . import user_db
from .db_init import Base, engine


Base.metadata.create_all(bind=engine)
