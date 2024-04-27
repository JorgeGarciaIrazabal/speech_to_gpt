from src.meal_organizer_2.db import user_db
from src.meal_organizer_2.db.db_init import Base, engine


Base.metadata.create_all(bind=engine)
