from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)
    is_active  = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites  = db.relationship("Favorite", back_populates="user",
                                 cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

    def serialize(self):
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat(),
            # never serialize the password!
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), unique=True, nullable=False)
    climate         = db.Column(db.String(120))
    terrain         = db.Column(db.String(120))
    population      = db.Column(db.String(50))
    diameter        = db.Column(db.String(50))
    gravity         = db.Column(db.String(80))
    orbital_period  = db.Column(db.String(50))
    rotation_period = db.Column(db.String(50))
    surface_water   = db.Column(db.String(50))

    residents       = db.relationship("Person", back_populates="homeworld", lazy=True)

    def __repr__(self):
        return f"<Planet {self.name}>"

    def serialize(self):
        return {
            "id":              self.id,
            "name":            self.name,
            "climate":         self.climate,
            "terrain":         self.terrain,
            "population":      self.population,
            "diameter":        self.diameter,
            "gravity":         self.gravity,
            "orbital_period":  self.orbital_period,
            "rotation_period": self.rotation_period,
            "surface_water":   self.surface_water,
        }


class Person(db.Model):
    __tablename__ = "person"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), unique=True, nullable=False)
    birth_year   = db.Column(db.String(50))
    eye_color    = db.Column(db.String(50))
    gender       = db.Column(db.String(50))
    hair_color   = db.Column(db.String(50))
    height       = db.Column(db.String(50))
    mass         = db.Column(db.String(50))
    skin_color   = db.Column(db.String(50))
    homeworld_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)

    homeworld    = db.relationship("Planet", back_populates="residents")

    def __repr__(self):
        return f"<Person {self.name}>"

    def serialize(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "birth_year":  self.birth_year,
            "eye_color":   self.eye_color,
            "gender":      self.gender,
            "hair_color":  self.hair_color,
            "height":      self.height,
            "mass":        self.mass,
            "skin_color":  self.skin_color,
            "homeworld":   self.homeworld.name if self.homeworld else None,
            "homeworld_id": self.homeworld_id,
        }


class Favorite(db.Model):
    __tablename__ = "favorite"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("user.id"),   nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=True)

    user      = db.relationship("User",   back_populates="favorites")
    planet    = db.relationship("Planet", lazy=True)
    person    = db.relationship("Person", lazy=True)

    def __repr__(self):
        return f"<Favorite user={self.user_id}>"

    def serialize(self):
        result = {"id": self.id, "user_id": self.user_id}
        if self.planet_id:
            result["type"] = "planet"
            result["item"] = self.planet.serialize() if self.planet else None
        elif self.person_id:
            result["type"] = "people"
            result["item"] = self.person.serialize() if self.person else None
        return result