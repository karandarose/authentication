from flask import jsonify, request

from db import db
from models.temples import Temples, temple_schema, temples_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank, authenticate_return_auth


@authenticate_with_rank('Grand Master')
def create_temple(auth_info):
    post_data = request.form if request.form else request.get_json()

    new_temple = Temples.new_temple_obj()
    populate_object(new_temple, post_data)

    try:
        db.session.add(new_temple)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to create temple: {e}"}), 400

    return jsonify({"message": "temple established", "result": temple_schema.dump(new_temple)}), 201


@authenticate_return_auth
def get_temple_by_id(temple_id, auth_info):
    temple_query = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()

    if not temple_query:
        return jsonify({"message": "temple not found"}), 404

    return jsonify({"message": "temple found", "result": temple_schema.dump(temple_query)}), 200


@authenticate_with_rank('Grand Master')
def update_temple(temple_id, auth_info):
    post_data = request.form if request.form else request.get_json()

    temple_query = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()

    if not temple_query:
        return jsonify({"message": "temple not found"}), 404

    populate_object(temple_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update temple: {e}"}), 400

    return jsonify({"message": "temple updated", "result": temple_schema.dump(temple_query)}), 200


@authenticate_with_rank('Grand Master')
def delete_temple(temple_id, auth_info):
    temple_query = db.session.query(Temples).filter(Temples.temple_id == temple_id).first()

    if not temple_query:
        return jsonify({"message": "temple not found"}), 404

    temple_query.is_active = False

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to deactivate temple: {e}"}), 400

    return jsonify({"message": "temple deactivated"}), 200
