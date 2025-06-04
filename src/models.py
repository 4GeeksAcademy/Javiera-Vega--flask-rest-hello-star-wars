from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    user_planet: Mapped[List["Favorites_Planets"]] = relationship(
        "favorites_planets",
        back_populates= "user_fav_planets")
    
    user_character: Mapped[List["Favorites_Characters"]] = relationship(
        "favorites_characters",
        back_populates= "user_fav_characters")
 
class Planets(db.Model):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String (500), nullable=False)

    fav_planets: Mapped[List["Favorites_Planets"]] = relationship(
        "favorites_planets",
        back_populates= "planets_favorites")

    fav_characters: Mapped[List["Favorites_Characters"]] = relationship(
        "favorites_characters",
        back_populates= "characters_favorites")

class Characters(db.Model):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String (500), nullable=False)

class Favorites_Planets(db.Model):
    __tablename__ = "favorites_planets"

    id: Mapped[int] = mapped_column(primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user_fav_planets: Mapped["User"] = relationship(back_populates= "user_planet")
    planets_favorites: Mapped["Planets"] = relationship(back_populates= "fav_planets")

class Favorites_Characters(db.Model):
    __tablename__ = "favorites_characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user_fav_characters: Mapped["User"] = relationship(back_populates= "user_character")
    characters_favorites: Mapped["Characters"] = relationship(back_populates= "fav_characters")









