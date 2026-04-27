from flask import Blueprint

import controllers

lightsaber = Blueprint('lightsaber', __name__)


@lightsaber.route('/lightsaber', methods=['POST'])
def create_lightsaber_route():
    return controllers.create_lightsaber()


@lightsaber.route('/lightsaber/<owner_id>', methods=['GET'])
def get_lightsaber_by_owner_route(owner_id):
    return controllers.get_lightsaber_by_owner(owner_id)


@lightsaber.route('/lightsaber/<saber_id>', methods=['PUT'])
def update_lightsaber_route(saber_id):
    return controllers.update_lightsaber(saber_id)


@lightsaber.route('/lightsaber/delete/<saber_id>', methods=['DELETE'])
def delete_lightsaber_route(saber_id):
    return controllers.delete_lightsaber(saber_id)
