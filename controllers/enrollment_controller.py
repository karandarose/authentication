from flask import jsonify, request

from db import db
from models.padawan_courses import PadawanCourses, enrollment_schema, enrollments_schema
from models.padawans import Padawans
from models.courses import Courses
from lib.authenticate import authenticate_with_rank


@authenticate_with_rank('Master')
def create_enrollment(auth_info):
    post_data = request.form if request.form else request.get_json()

    padawan_id = post_data.get('padawan_id')
    course_id = post_data.get('course_id')

    padawan_query = db.session.query(Padawans).filter(Padawans.padawan_id == padawan_id).first()
    course_query = db.session.query(Courses).filter(Courses.course_id == course_id).first()

    if not padawan_query:
        return jsonify({"message": "padawan not found"}), 404

    if not course_query:
        return jsonify({"message": "course not found"}), 404

    existing_enrollment = db.session.query(PadawanCourses).filter(
        PadawanCourses.padawan_id == padawan_id,
        PadawanCourses.course_id == course_id
    ).first()

    if existing_enrollment:
        return jsonify({"message": "padawan already enrolled in this course"}), 400

    new_enrollment = PadawanCourses(padawan_id=padawan_id, course_id=course_id)

    try:
        db.session.add(new_enrollment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to enroll padawan: {e}"}), 400

    return jsonify({"message": "padawan enrolled", "result": enrollment_schema.dump(new_enrollment)}), 201


@authenticate_with_rank('Youngling')
def delete_enrollment(padawan_id, course_id, auth_info):
    enrollment_query = db.session.query(PadawanCourses).filter(
        PadawanCourses.padawan_id == padawan_id,
        PadawanCourses.course_id == course_id
    ).first()

    if not enrollment_query:
        return jsonify({"message": "enrollment not found"}), 404

    try:
        db.session.delete(enrollment_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"unable to remove enrollment: {e}"}), 400

    return jsonify({"message": "padawan removed from course"}), 200
