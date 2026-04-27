from flask import jsonify, request

from db import db
from models.padawans import Padawans, padawan_schema, padawans_schema
from models.masters import Masters
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank, FORCE_RANKS


@authenticate_with_rank('Master')
def create_padawan(auth_info):
    post_data = request.form if request.form else request.get_json()

    new_padawan = Padawans.new_padawan_obj()
    populate_object(new_padawan, post_data)

    try:
        db.session.add(new_padawan)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to create padawan: {e}"}), 400

    return jsonify({"message": "padawan created", "result": padawan_schema.dump(new_padawan)}), 201


@authenticate_with_rank('Master')
def get_padawans(auth_info):
    padawans_query = db.session.query(Padawans).all()

    if not padawans_query:
        return jsonify({"message": "no padawans found"}), 404

    return jsonify({"message": "padawans found", "results": padawans_schema.dump(padawans_query)}), 200


@authenticate_with_rank('Youngling')
def get_active_padawans(auth_info):
    padawans_query = db.session.query(Padawans).filter(Padawans.graduation_date == None).all()

    if not padawans_query:
        return jsonify({"message": "no active padawans found"}), 404

    return jsonify({"message": "active padawans found", "results": padawans_schema.dump(padawans_query)}), 200


@authenticate_with_rank('Youngling')
def update_padawan(padawan_id, auth_info):
    post_data = request.form if request.form else request.get_json()

    padawan_query = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()

    if not padawan_query:
        return jsonify({"message": "padawan not found"}), 404

    is_council_plus = FORCE_RANKS.index(auth_info.user.force_rank) >= FORCE_RANKS.index('Council')

    assigned_master = db.session.query(Masters).filter(
        Masters.master_id == padawan_query.master_id,
        Masters.user_id == auth_info.user_id
    ).first()

    if not assigned_master and not is_council_plus:
        return jsonify({"message": "unauthorized"}), 403

    populate_object(padawan_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update padawan: {e}"}), 400

    return jsonify({"message": "padawan updated", "result": padawan_schema.dump(padawan_query)}), 200


@authenticate_with_rank('Council')
def delete_padawan(padawan_id, auth_info):
    padawan_query = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()

    if not padawan_query:
        return jsonify({"message": "padawan not found"}), 404

    try:
        db.session.delete(padawan_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to remove padawan: {e}"}), 400

    return jsonify({"message": "padawan record removed"}), 200


@authenticate_with_rank('Council')
def promote_padawan(padawan_id, auth_info):
    from datetime import datetime

    padawan_query = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()

    if not padawan_query:
        return jsonify({"message": "padawan not found"}), 404

    padawan_query.graduation_date = datetime.now()

    if padawan_query.user_id:
        from models.users import Users
        user_query = db.session.query(Users).filter(Users.user_id == padawan_query.user_id).first()
        if user_query:
            user_query.force_rank = 'Knight'

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to promote padawan: {e}"}), 400

    return jsonify({"message": "padawan promoted to knight", "result": padawan_schema.dump(padawan_query)}), 200
