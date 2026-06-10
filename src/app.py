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
from models import db, User, Planet, Person, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# ── Handle/serialize errors like a JSON object ────────────────────────────────
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"message": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return jsonify({"message": "Internal server error"}), 500


# ── Sitemap ───────────────────────────────────────────────────────────────────
@app.route('/')
def sitemap():
    return generate_sitemap(app)



# PEOPLE


@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = db.session.get(Person, people_id)
    if person is None:
        raise APIException(f"Person with id {people_id} not found", status_code=404)
    return jsonify(person.serialize()), 200



# PLANETS


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        raise APIException(f"Planet with id {planet_id} not found", status_code=404)
    return jsonify(planet.serialize()), 200



# USERS


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # No auth system yet — identify current user via header X-Current-User: <id>
    user_id = request.headers.get("X-Current-User", "").strip()
    if not user_id:
        raise APIException("Missing header 'X-Current-User'", status_code=400)
    if not user_id.isdigit():
        raise APIException(f"'X-Current-User' must be an integer, got: '{user_id}'", status_code=400)

    user = db.session.get(User, int(user_id))
    if user is None:
        raise APIException(f"User with id {user_id} not found", status_code=404)
    if not user.is_active:
        raise APIException(f"User with id {user_id} is deactivated", status_code=403)

    return jsonify([f.serialize() for f in user.favorites]), 200



# FAVORITES — PLANET


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # No auth system yet — identify current user via header X-Current-User: <id>
    user_id = request.headers.get("X-Current-User", "").strip()
    if not user_id:
        raise APIException("Missing header 'X-Current-User'", status_code=400)
    if not user_id.isdigit():
        raise APIException(f"'X-Current-User' must be an integer, got: '{user_id}'", status_code=400)

    user = db.session.get(User, int(user_id))
    if user is None:
        raise APIException(f"User with id {user_id} not found", status_code=404)
    if not user.is_active:
        raise APIException(f"User with id {user_id} is deactivated", status_code=403)

    planet = db.session.get(Planet, planet_id)
    if planet is None:
        raise APIException(f"Planet with id {planet_id} not found", status_code=404)

    already = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if already:
        raise APIException(f"Planet '{planet.name}' is already in your favorites", status_code=409)

    fav = Favorite(user_id=user.id, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # No auth system yet — identify current user via header X-Current-User: <id>
    user_id = request.headers.get("X-Current-User", "").strip()
    if not user_id:
        raise APIException("Missing header 'X-Current-User'", status_code=400)
    if not user_id.isdigit():
        raise APIException(f"'X-Current-User' must be an integer, got: '{user_id}'", status_code=400)

    user = db.session.get(User, int(user_id))
    if user is None:
        raise APIException(f"User with id {user_id} not found", status_code=404)
    if not user.is_active:
        raise APIException(f"User with id {user_id} is deactivated", status_code=403)

    fav = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if fav is None:
        raise APIException(f"No favorite found for planet id {planet_id}", status_code=404)

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": f"Planet {planet_id} removed from favorites"}), 200



# FAVORITES — PEOPLE


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    # No auth system yet — identify current user via header X-Current-User: <id>
    user_id = request.headers.get("X-Current-User", "").strip()
    if not user_id:
        raise APIException("Missing header 'X-Current-User'", status_code=400)
    if not user_id.isdigit():
        raise APIException(f"'X-Current-User' must be an integer, got: '{user_id}'", status_code=400)

    user = db.session.get(User, int(user_id))
    if user is None:
        raise APIException(f"User with id {user_id} not found", status_code=404)
    if not user.is_active:
        raise APIException(f"User with id {user_id} is deactivated", status_code=403)

    person = db.session.get(Person, people_id)
    if person is None:
        raise APIException(f"Person with id {people_id} not found", status_code=404)

    already = Favorite.query.filter_by(user_id=user.id, person_id=people_id).first()
    if already:
        raise APIException(f"'{person.name}' is already in your favorites", status_code=409)

    fav = Favorite(user_id=user.id, person_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    # No auth system yet — identify current user via header X-Current-User: <id>
    user_id = request.headers.get("X-Current-User", "").strip()
    if not user_id:
        raise APIException("Missing header 'X-Current-User'", status_code=400)
    if not user_id.isdigit():
        raise APIException(f"'X-Current-User' must be an integer, got: '{user_id}'", status_code=400)

    user = db.session.get(User, int(user_id))
    if user is None:
        raise APIException(f"User with id {user_id} not found", status_code=404)
    if not user.is_active:
        raise APIException(f"User with id {user_id} is deactivated", status_code=403)

    fav = Favorite.query.filter_by(user_id=user.id, person_id=people_id).first()
    if fav is None:
        raise APIException(f"No favorite found for person id {people_id}", status_code=404)

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": f"Person {people_id} removed from favorites"}), 200


# ── this only runs if `$ python src/app.py` is executed ──────────────────────
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)