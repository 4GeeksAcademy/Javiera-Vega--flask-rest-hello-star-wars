from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    user_planet: Mapped[List["Favorites_Planet"]] = relationship(
        back_populates= "user_fav_planet")
    
    user_people: Mapped[List["Favorites_People"]] = relationship(
        back_populates= "user_fav_people")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "password": self.password
        }
 
class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String (500), nullable=False)

    fav_planet: Mapped[List["Favorites_Planet"]] = relationship(
        back_populates= "planet_favorites")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class People(db.Model):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String (500), nullable=False)

    fav_people: Mapped[List["Favorites_People"]] = relationship(
        back_populates= "people_favorites")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class Favorites_Planet(db.Model):
    __tablename__ = "favorites_planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user_fav_planet: Mapped["User"] = relationship(back_populates= "user_planet")
    planet_favorites: Mapped["Planet"] = relationship(back_populates= "fav_planet")

class Favorites_People(db.Model):
    __tablename__ = "favorites_people"

    id: Mapped[int] = mapped_column(primary_key=True)
    people_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user_fav_people: Mapped["User"] = relationship(back_populates= "user_people")
    people_favorites: Mapped["People"] = relationship(back_populates= "fav_people")









