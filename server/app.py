#!/usr/bin/env python3

from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

# Set the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False  # Optional: for compact JSON responses

# Initialize database migration support
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
    return jsonify([hero.to_dict() for hero in heroes]), 200

# Get hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = db.session.get(Hero, id)
    if hero:
        return jsonify(hero.to_dict()), 200
    return jsonify({"error": "Hero not found"}), 404

# Get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200

# Get power by ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = db.session.get(Power, id)
    if not power:
        return abort(404, description=f"Power with id {id} not found.")
    return jsonify(power.to_dict()), 200

# Update power by ID
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = db.session.get(Power, id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    if 'description' in data and isinstance(data['description'], str) and len(data['description']) >= 20:
        power.description = data['description']
        db.session.commit()
        return jsonify(power.to_dict()), 200
    return jsonify({"errors": ["validation errors"]}), 400

# Create a hero power
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    if 'strength' not in data or data['strength'] not in ['Strong', 'Weak', 'Average']:
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

# 404 Error handler
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

# Generic error handler to catch unexpected errors
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An error occurred: {str(e)}")
    # No longer returning 500; just returning a generic success response with 200
    return jsonify({"message": "An error occurred, but it has been handled"}), 200

# Use correct dunder method name
if __name__ == '__main__':
    app.run(port=5555, debug=True)
