"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# Usuarios


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    favorites = {
        "favorite_characters": [c.serialize() for c in user.favorite_characters],
        "favorite_planets": [p.serialize() for p in user.favorite_planets]
    }
    return jsonify(favorites), 200


# People
@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    person = Character.query.get(people_id)
    if not person:
        return jsonify({"msg": "Character not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    person = Character.query.get(people_id)
    if not user or not person:
        return jsonify({"error": "Usuario o Personaje no encontrado"}), 404
    if person in user.favorite_characters:
        return jsonify({"msg": "El personaje ya está en favoritos"}), 200
    user.favorite_characters.append(person)
    db.session.commit()
    return jsonify({"msg": "Personaje agregado a favoritos"}), 201


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    person = Character.query.get(people_id)
    if not user or not person:
        return jsonify({"error": "Usuario o Personaje no encontrado"}), 404
    if person not in user.favorite_characters:
        return jsonify({"msg": "El personaje no está en favoritos"}), 200
    user.favorite_characters.remove(person)
    db.session.commit()
    return jsonify({"msg": "Personaje borrado de favoritos"}), 201

# Planets


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({"error": "Usuario o Planeta no encontrado"}), 404
    if planet in user.favorite_planets:
        return jsonify({"msg": "El planeta ya está en favoritos"}), 200
    user.favorite_planets.append(planet)
    db.session.commit()
    return jsonify({"msg": "Planeta agregado a favoritos"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({"error": "Usuario o Planeta no encontrado"}), 404
    if planet not in user.favorite_planets:
        return jsonify({"msg": "El planeta no está en favoritos"}), 200
    user.favorite_planets.remove(planet)
    db.session.commit()
    return jsonify({"msg": "Planeta borrado de favoritos"}), 201


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
