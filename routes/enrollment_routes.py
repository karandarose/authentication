from flask import Blueprint

import controllers

enrollment = Blueprint('enrollment', __name__)


@enrollment.route('/enrollment', methods=['POST'])
def create_enrollment_route():
    return controllers.create_enrollment()


@enrollment.route('/enrollment/<padawan_id>/<course_id>', methods=['DELETE'])
def delete_enrollment_route(padawan_id, course_id):
    return controllers.delete_enrollment(padawan_id, course_id)
