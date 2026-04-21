from flask import jsonify, request

from db import db
from models.warranty import Warranties, warranty_schema, warranties_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth

def create_warranty():
    post_data = request.form if request.form else request.get_json()

    new_warranty = Warranties.new_warranty_obj()
    populate_object(new_warranty, post_data)

    try:
        db.session.add(new_warranty)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to create warranty: {e}"}), 400

    return jsonify({"message": "warranty created", "result": warranty_schema.dump(new_warranty)}), 201

def get_warranties():
    warranty_query = db.session.query(Warranties).all()

    if not warranty_query:
        return jsonify({"message": "no warranties found"}), 404

    return jsonify({"message": "warranties found", "results": warranties_schema.dump(warranty_query)}), 200


def get_warranty_by_id(warranty_id):
    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    if not warranty_query:
        return jsonify({"message": "warranty not found"}), 404

    return jsonify({"message": "warranty found", "result": warranty_schema.dump(warranty_query)}), 200

def update_warranty_by_id(warranty_id):
    post_data = request.form if request.form else request.get_json()
    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    if not warranty_query:
        return jsonify({"message": "warranty not found"}), 404

    populate_object(warranty_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update warranty: {e}"}), 400

    return jsonify({"message": "warranty updated", "result": warranty_schema.dump(warranty_query)}), 200

def delete_warranty_by_id(warranty_id):
    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    if not warranty_query:
        return jsonify({"message": "warranty not found"}), 404

    try:
        db.session.delete(warranty_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to delete warranty: {e}"}), 400

    return jsonify({"message": "warranty deleted"}), 200