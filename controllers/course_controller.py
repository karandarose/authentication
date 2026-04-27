from flask import jsonify, request

from db import db
from models.courses import Courses, course_schema, courses_schema
from models.masters import Masters
from util.reflection import populate_object
from lib.authenticate import authenticate_with_rank, FORCE_RANKS


@authenticate_with_rank('Master')
def create_course(auth_info):
    post_data = request.form if request.form else request.get_json()

    new_course = Courses.new_course_obj()
    populate_object(new_course, post_data)

    try:
        db.session.add(new_course)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to create course: {e}"}), 400

    return jsonify({"message": "course created", "result": course_schema.dump(new_course)}), 201


@authenticate_with_rank('Youngling')
def get_courses_by_difficulty(difficulty_level, auth_info):
    courses_query = db.session.query(Courses).filter(Courses.difficulty == difficulty_level).all()

    if not courses_query:
        return jsonify({"message": "no courses found at this difficulty"}), 404

    return jsonify({"message": "courses found", "results": courses_schema.dump(courses_query)}), 200


@authenticate_with_rank('Youngling')
def update_course(course_id, auth_info):
    post_data = request.form if request.form else request.get_json()

    course_query = db.session.query(Courses).filter(Courses.course_id == course_id).first()

    if not course_query:
        return jsonify({"message": "course not found"}), 404

    is_council_plus = FORCE_RANKS.index(auth_info.user.force_rank) >= FORCE_RANKS.index('Council')

    instructor = db.session.query(Masters).filter(
        Masters.master_id == course_query.instructor_id,
        Masters.user_id == auth_info.user_id
    ).first()

    if not instructor and not is_council_plus:
        return jsonify({"message": "unauthorized"}), 403

    populate_object(course_query, post_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to update course: {e}"}), 400

    return jsonify({"message": "course updated", "result": course_schema.dump(course_query)}), 200


@authenticate_with_rank('Youngling')
def delete_course(course_id, auth_info):
    course_query = db.session.query(Courses).filter(Courses.course_id == course_id).first()

    if not course_query:
        return jsonify({"message": "course not found"}), 404

    is_council_plus = FORCE_RANKS.index(auth_info.user.force_rank) >= FORCE_RANKS.index('Council')

    instructor = db.session.query(Masters).filter(
        Masters.master_id == course_query.instructor_id,
        Masters.user_id == auth_info.user_id
    ).first()

    if not instructor and not is_council_plus:
        return jsonify({"message": "unauthorized"}), 403

    try:
        db.session.delete(course_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to cancel course: {e}"}), 400

    return jsonify({"message": "course cancelled"}), 200
