from flask import jsonify, request

from db import db
from models.species import Species, species_schema, species_list_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank


@authenticate_with_rank('Master')
def create_species(auth_info):
    post_data = request.form if request.form else request.get_json()

    new_species = Species.new_species_obj()
    populate_object(new_species, post_data)

    try:
        db.session.add(new_species)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to document species: {e}"}), 400

    return jsonify({"message": "species documented", "result": species_schema.dump(new_species)}), 201


@authenticate_with_rank('Youngling')
def get_species_by_id(species_id, auth_info):
    species_query = db.session.query(Species).filter(Species.species_id == species_id).first()

    if not species_query:
        return jsonify({"message": "species not found"}), 404

    return jsonify({"message": "species found", "result": species_schema.dump(species_query)}), 200
