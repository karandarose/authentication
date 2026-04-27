from flask import Blueprint

import controllers

course = Blueprint('course', __name__)


@course.route('/course', methods=['POST'])
def create_course_route():
    return controllers.create_course()


@course.route('/courses/<difficulty_level>', methods=['GET'])
def get_courses_by_difficulty_route(difficulty_level):
    return controllers.get_courses_by_difficulty(difficulty_level)


@course.route('/course/<course_id>', methods=['PUT'])
def update_course_route(course_id):
    return controllers.update_course(course_id)


@course.route('/course/delete/<course_id>', methods=['DELETE'])
def delete_course_route(course_id):
    return controllers.delete_course(course_id)
