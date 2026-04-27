from flask import jsonify, request

from db import db
from models.masters import Masters, master_schema, masters_schema
from models.users import Users
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank, FORCE_RANKS


@authenticate_with_rank('Council')
def create_master(auth_info):
    post_data = request.form if request.form else request.get_json()

    user_id = post_data.get('user_id')
    user_query = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_query:
        return jsonify({"message": "user not found"}), 404

    new_master = Masters.new_master_obj()
    populate_object(new_master, post_data)

    user_query.force_rank = 'Master'

    try:
        db.session.add(new_master)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to promote to master: {e}"}), 400

    return jsonify({"message": "master promoted", "result": master_schema.dump(new_master)}), 201


@authenticate_with_rank('Padawan')
def get_masters(auth_info):
    masters_query = db.session.query(Masters).all()

    if not masters_query:
        return jsonify({"message": "no masters found"}), 404

    return jsonify({"message": "masters found", "results": masters_schema.dump(masters_query)}), 200


@authenticate_with_rank('Youngling')
def update_master(master_id, auth_info):
    post_data = request.form if request.form else request.get_json()

    master_query = db.session.query(Masters).filter(Masters.master_id == master_id).first()

    if not master_query:
        return jsonify({"message": "master not found"}), 404

    is_council_plus = FORCE_RANKS.index(auth_info.user.force_rank) >= FORCE_RANKS.index('Council')
    is_self = str(master_query.user_id) == str(auth_info.user_id)

    if not is_self and not is_council_plus:
        return jsonify({"message": "unauthorized"}), 403

    populate_object(master_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update master: {e}"}), 400

    return jsonify({"message": "master updated", "result": master_schema.dump(master_query)}), 200


@authenticate_with_rank('Grand Master')
def delete_master(master_id, auth_info):
    master_query = db.session.query(Masters).filter(Masters.master_id == master_id).first()

    if not master_query:
        return jsonify({"message": "master not found"}), 404

    try:
        db.session.delete(master_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to remove master: {e}"}), 400

    return jsonify({"message": "master status removed"}), 200
