from flask import jsonify, request

from db import db
from models.company import Companies, company_schema, companies_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth, authenticate

@authenticate
def add_company():
    post_data = request.form if request.form else request.json

    new_company = Companies.new_company_obj()

    populate_object(new_company, post_data)

    db.session.add(new_company)
    db.session.commit()

    return jsonify({"message": "company created", "result": company_schema.dump(new_company)}), 201

@authenticate_return_auth
def get_all_companies(auth_info):
    if auth_info.user.role == 'super-admin':
        companies_query = db.session.query(Companies).all()

        return jsonify({"message": "companies found", "results": companies_schema.dump(companies_query)}), 200
    
    return jsonify({"message": "unauthorized"}), 401

def get_company_by_id(company_id):
    company_query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    if not company_query:
        return jsonify({"message": "company not found"}), 404

    return jsonify({"message": "company found", "result": company_schema.dump(company_query)}), 200

def update_company_by_id(company_id):
    post_data = request.form if request.form else request.get_json()
    company_query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    if not company_query:
        return jsonify({"message": "company not found"}), 404

    populate_object(company_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update company: {e}"}), 400

    return jsonify({"message": "company updated", "result": company_schema.dump(company_query)}), 200

def delete_company_by_id(company_id):
    company_query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    if not company_query:
        return jsonify({"message": "company not found"}), 404

    try:
        db.session.delete(company_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to delete company: {e}"}), 400

    return jsonify({"message": "company deleted"}), 200