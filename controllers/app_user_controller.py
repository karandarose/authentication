from flask import jsonify, request
from flask_bcrypt import generate_password_hash

from db import db
from models.app_users import AppUsers, app_user_schema, app_users_schema
from models.organizations import Organizations
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth, authenticate

def add_user():
    post_data = request.form if request.form else request.json
    org_id = post_data.get('org_id')

    new_user = AppUsers.new_user_obj()

    populate_object(new_user, post_data)

    new_user.password = generate_password_hash(new_user.password).decode('utf8')

    if org_id:
        org_query = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

        if org_query == None:
            return jsonify({"message": "org_id is required"}), 400
        
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "user created", "result": app_user_schema.dump(new_user)}), 201

@authenticate
def users_get_all():
    users_query = db.session.query(AppUsers).all()

    return jsonify({"message": "users found", "results": app_users_schema.dump(users_query)}), 200

@authenticate_return_auth
def user_get_by_id(user_id, auth_info):
    user_query = db.session.query(AppUsers).filter(AppUsers.user_id == user_id).first()

    if auth_info.user.role == 'super-admin' or user_id == str(auth_info.user.user_id):
        return jsonify({"message": "user found", "result": app_user_schema.dump(user_query)}), 200
    
    return jsonify({"message": "unauthorized"}), 401