from flask import Blueprint, jsonify, request
from api.models import db, User, People, Planet, Favorite

api = Blueprint("api", __name__)


CURRENT_USER_ID = 1
@api.route("/people", methods=["GET"])
def get_all_people():
    people = People.query.all()

    return jsonify([person.serialize() for person in people]), 200


@api.route("/people/<int:people_id>", methods=["GET"])
def get_one_people(people_id):
    person = People.query.get(people_id)

    if person is None:
        return jsonify({"msg": "People not found"}), 404

    return jsonify(person.serialize()), 200
@api.route("/planets", methods=["GET"])
def get_all_planets():
    planets = Planet.query.all()

    return jsonify([planet.serialize() for planet in planets]), 200


@api.route("/planets/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200
@api.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    return jsonify([user.serialize() for user in users]), 200
@api.route("/users/favorites", methods=["GET"])
def get_user_favorites():
    user = User.query.get(CURRENT_USER_ID)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    favorites = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()

    return jsonify([favorite.serialize() for favorite in favorites]), 200
@api.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    user = User.query.get(CURRENT_USER_ID)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id
    ).first()

    if existing_favorite:
        return jsonify({"msg": "Planet already in favorites"}), 400

    new_favorite = Favorite(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "msg": "Planet added to favorites",
        "favorite": new_favorite.serialize()
    }), 201
@api.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    user = User.query.get(CURRENT_USER_ID)

    if user is None:
        return jsonify({"msg": "User not found"}), 404

    person = People.query.get(people_id)

    if person is None:
        return jsonify({"msg": "People not found"}), 404

    existing_favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        people_id=people_id
    ).first()

    if existing_favorite:
        return jsonify({"msg": "People already in favorites"}), 400

    new_favorite = Favorite(
        user_id=CURRENT_USER_ID,
        people_id=people_id
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "msg": "People added to favorites",
        "favorite": new_favorite.serialize()
    }), 201
@api.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        planet_id=planet_id
    ).first()

    if favorite is None:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Planet removed from favorites"}), 200
@api.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    favorite = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID,
        people_id=people_id
    ).first()

    if favorite is None:
        return jsonify({"msg": "Favorite people not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "People removed from favorites"}), 200