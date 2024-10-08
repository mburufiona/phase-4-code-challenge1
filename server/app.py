#!/usr/bin/env python3

from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Hero, Power, HeroPower
import os

# Fix: Use correct dunder method name
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:////{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False  # Optional: Remove this if it causes issues

migrate = Migrate(app, db)

db.init_app(app)

# Index route
@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

# Get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{'id': hero.id, 'name': hero.name, 'super_name': hero.super_name} for hero in heroes])

# Get hero by id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    with app.app_context():
        hero = db.session.get(Hero, id)
        if hero:
            return jsonify(hero.to_dict()), 200
        return jsonify({"error": "Hero not found"}), 404

# Get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200

# Get power by id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = db.session.get(Power, id)
    if power is None:
        abort(404, description=f"Power with id {id} not found.")
    return jsonify(power.to_dict()), 200

# Update power by id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = db.session.get(Power, id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    if 'description' in data:
        if not isinstance(data['description'], str) or len(data['description']) < 20:
            return jsonify({"errors": ["validation errors"]}), 400
        power.description = data['description']

    db.session.commit()
    return jsonify(power.to_dict()), 200

# Create a hero power
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    try:
        data = request.get_json()

        if 'strength' not in data or data['strength'] not in ['Strong', 'Weak', 'Average']:
            return jsonify({"errors": ["validation errors"]}), 400

        if 'hero_id' not in data or 'power_id' not in data:
            return jsonify({"errors": ["validation errors"]}), 400

        hero = db.session.get(Hero, data['hero_id'])
        power = db.session.get(Power, data['power_id'])

        if not hero or not power:
            return jsonify({"errors": ["validation errors"]}), 400

        hero_power = HeroPower(
            hero_id=hero.id,
            power_id=power.id,
            strength=data['strength']
        )

        db.session.add(hero_power)
        db.session.commit()

        response = {
            "id": hero_power.id,
            "hero_id": hero.id,
            "power_id": power.id,
            "strength": hero_power.strength,
            "hero": {"id": hero.id, "name": hero.name, "super_name": hero.super_name},
            "power": {"id": power.id, "name": power.name}
        }

        return jsonify(response), 200
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        db.session.rollback()
        return jsonify({"errors": ["An unexpected error occurred"]}), 500

# 404 Error handler
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

# Fix: Use correct dunder method name
if __name__ == '__main__':
    app.run(port=5555, debug=True)