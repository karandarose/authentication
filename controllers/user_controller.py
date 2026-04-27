from flask import jsonify, request
from flask_bcrypt import generate_password_hash

from db import db
from models.users import Users, user_schema, users_schema
from util.reflection import populate_object
from lib.authenticate import authenticate_return_auth, authenticate, authenticate_with_rank

def add_user():
    post_data = request.form if request.form else request.json
    password = post_data.get("password")

    new_user = Users.new_user_obj()

    populate_object(new_user, post_data)

    new_user.password = generate_password_hash(password).decode('utf8')

        
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "user created", "result": user_schema.dump(new_user)}), 201

@authenticate_with_rank('Council')
def users_get_all():
    users_query = db.session.query(Users).all()

    return jsonify({"message": "users found", "results": users_schema.dump(users_query)}), 200

@authenticate_return_auth
def user_get_by_id(user_id, auth_info):
    user_query = db.session.query(Users).filter(Users.user_id == user_id).first()

    if auth_info.user.role == 'super-admin' or user_id == str(auth_info.user.user_id):
        return jsonify({"message": "user found", "result": user_schema.dump(user_query)}), 200
    
    return jsonify({"message": "unauthorized"}), 401

@authenticate_return_auth
def update_user_by_id(user_id, auth_info):
    post_data = request.form if request.form else request.get_json()
    user_query = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user_query and auth_info.user.role == 'super-admin' or user_id == str(auth_info.user.user_id):
        populate_object(user_query, post_data)
        db.session.commit()
        return jsonify({"message": "user updated", "result": user_schema.dump(user_query)}), 200
    
    return jsonify({"message": "unauthorized"})

@authenticate_with_rank('Grand_Master')
def delete_user_by_id(user_id, auth_info):
    user_query = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_query:
        return jsonify({"message" : "user not found"}), 404
    
    if auth_info.user.role == 'super-admin':
        try:
            db.session.detely(user_query)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"unable to delete user {e}, unauthorized"}), 400
    
    return jsonify({"message": "user deleted"}), 200