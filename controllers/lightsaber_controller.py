from flask import jsonify, request

from db import db
from models.lightsabers import Lightsabers, lightsaber_schema, lightsabers_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank, FORCE_RANKS


@authenticate_with_rank('Padawan')
def create_lightsaber(auth_info):
    post_data = request.form if request.form else request.get_json()

    new_lightsaber = Lightsabers.new_lightsaber_obj()
    populate_object(new_lightsaber, post_data)

    try:
        db.session.add(new_lightsaber)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to begin lightsaber construction: {e}"}), 400

    return jsonify({"message": "lightsaber construction begun", "result": lightsaber_schema.dump(new_lightsaber)}), 201


@authenticate_with_rank('Youngling')
def get_lightsaber_by_owner(owner_id, auth_info):
    saber_query = db.session.query(Lightsabers).filter(Lightsabers.owner_id == owner_id).all()

    if not saber_query:
        return jsonify({"message": "no lightsabers found for this owner"}), 404

    return jsonify({"message": "lightsabers found", "results": lightsabers_schema.dump(saber_query)}), 200


@authenticate_with_rank('Youngling')
def update_lightsaber(saber_id, auth_info):
    post_data = request.form if request.form else request.get_json()

    saber_query = db.session.query(Lightsabers).filter(Lightsabers.saber_id == saber_id).first()

    if not saber_query:
        return jsonify({"message": "lightsaber not found"}), 404

    if str(saber_query.owner_id) != str(auth_info.user_id):
        return jsonify({"message": "only the owner may modify their lightsaber"}), 403

    populate_object(saber_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update lightsaber: {e}"}), 400

    return jsonify({"message": "lightsaber updated", "result": lightsaber_schema.dump(saber_query)}), 200


@authenticate_with_rank('Youngling')
def delete_lightsaber(saber_id, auth_info):
    saber_query = db.session.query(Lightsabers).filter(Lightsabers.saber_id == saber_id).first()

    if not saber_query:
        return jsonify({"message": "lightsaber not found"}), 404

    is_council_plus = FORCE_RANKS.index(auth_info.user.force_rank) >= FORCE_RANKS.index('Council')
    is_owner = str(saber_query.owner_id) == str(auth_info.user_id)

    if not is_owner and not is_council_plus:
        return jsonify({"message": "unauthorized"}), 403

    try:
        db.session.delete(saber_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to destroy lightsaber record: {e}"}), 400

    return jsonify({"message": "lightsaber record destroyed"}), 200
