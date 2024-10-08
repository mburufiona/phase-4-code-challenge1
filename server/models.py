from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates

# Using a naming convention for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Hero Model
class Hero(db.Model):
    __tablename__ = 'heroes'  # Fix: Use double underscores for __tablename__
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    super_name = db.Column(db.String(100), nullable=False)
    hero_powers = db.relationship('HeroPower', backref='hero', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'super_name': self.super_name,
            'hero_powers': [hp.to_dict() for hp in self.hero_powers]
        }

    def __repr__(self):  # Fix: Use double underscores for __repr__
        return f'<Hero {self.id}>'


# Power Model
class Power(db.Model):
    __tablename__ = 'powers'  # Fix: Use double underscores for __tablename__
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    def __init__(self, name, description):  # Fix: Use double underscores for __init__
        self.name = name
        if not isinstance(description, str) or len(description) < 20:
            raise ValueError('Description must be a string of at least 20 characters')
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

    def __repr__(self):  # Fix: Use double underscores for __repr__
        return f'<Power {self.id}>'


# HeroPower Model
class HeroPower(db.Model):
    __tablename__ = 'hero_powers'  # Fix: Use double underscores for __tablename__
    
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(10), nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'strength': self.strength,
            'hero_id': self.hero_id,
            'power_id': self.power_id,
        }

    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError('Strength must be Strong, Weak, or Average')
        return strength

    def __repr__(self):  # Fix: Use double underscores for __repr__
        return f'<HeroPower {self.id}>'