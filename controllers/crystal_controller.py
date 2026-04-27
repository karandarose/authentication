from flask import jsonify, request

from db import db
from models.crystals import Crystals, crystal_schema, crystals_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank


@authenticate_with_rank('Master')
def create_crystal(auth_info):
    post_data = request.form if request.form else request.get_json()

    new_crystal = Crystals.new_crystal_obj()
    populate_object(new_crystal, post_data)

    try:
        db.session.add(new_crystal)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to catalog crystal: {e}"}), 400

    return jsonify({"message": "crystal cataloged", "result": crystal_schema.dump(new_crystal)}), 201


@authenticate_with_rank('Master')
def get_crystals_by_rarity(rarity_level, auth_info):
    crystals_query = db.session.query(Crystals).filter(Crystals.rarity_level == rarity_level).all()

    if not crystals_query:
        return jsonify({"message": "no crystals found at this rarity level"}), 404

    return jsonify({"message": "crystals found", "results": crystals_schema.dump(crystals_query)}), 200
