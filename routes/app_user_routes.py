from flask import Blueprint

import controllers

users = Blueprint('users', __name__)

@users.route('/user', methods=['POST'])
def add_user_route():
    return controllers.add_user()

@users.route('/users', methods=['GET'])
def users_get_all_route():
    return controllers.users_get_all()

@users.route('/user/<user_id>', methods=['GET'])
def user_get_by_id_route(user_id):
    return controllers.user_get_by_id(user_id)