from sqlalchemy import Column, Integer, String, ForeignKey

from src.meal_organizer_2.db.db_init import Base
from typing import Callable, Iterator
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session, relationship

from src.meal_organizer_2.db.errors import UserNotFoundError


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    ingredients = Column(String, nullable=False)
    instructions = Column(String, nullable=False)
    owned_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User")


class RecipeRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def get_all(self) -> Iterator[Recipe]:
        with self.session_factory() as session:
            return session.query(Recipe).all()

    def get_by_id(self, recipe_id: int) -> Recipe:
        with self.session_factory() as session:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                raise UserNotFoundError(recipe_id)
            return recipe

    def get_by_name(self, name: str) -> Recipe:
        with self.session_factory() as session:
            recipe = session.query(Recipe).filter(Recipe.name == name).first()
            if not recipe:
                raise UserNotFoundError(name)
            return recipe

    def add(
        self, name: str, description: str, ingredients: str, instructions: str
    ) -> Recipe:
        try:
            self.get_by_name(name)
            raise ValueError(f"Recipe with name {name} already exists")
        except UserNotFoundError:
            pass

        with self.session_factory() as session:
            recipe = Recipe(
                name=name,
                description=description,
                ingredients=ingredients,
                instructions=instructions,
            )
            session.add(recipe)
            session.commit()
            session.refresh(recipe)
            return recipe

    def delete_by_id(self, recipe_id: int) -> None:
        with self.session_factory() as session:
            entity: Recipe = (
                session.query(Recipe).filter(Recipe.id == recipe_id).first()
            )
            if not entity:
                raise UserNotFoundError(recipe_id)
            session.delete(entity)
            session.commit()

    def update(
        self,
        recipe_id: int,
        name: str,
        description: str,
        ingredients: str,
        instructions: str,
    ) -> Recipe:
        with self.session_factory() as session:
            recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not recipe:
                raise UserNotFoundError(recipe_id)
            recipe.name = name
            recipe.description = description
            recipe.ingredients = ingredients
            recipe.instructions = instructions
            session.commit()
            session.refresh(recipe)
            return recipe
