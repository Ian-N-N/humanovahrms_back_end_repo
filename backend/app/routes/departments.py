from flask import Blueprint, request, jsonify
from app.models import db, Department
from app.rbac import admin_only, hr_only

departments_bp = Blueprint("departments", __name__)

@departments_bp.route("/", methods=["GET"])
@hr_only
def list_departments():
    departments = Department.query.all()
    return jsonify(
        [{"id": d.id, "name": d.name} for d in departments]
    ), 200

@departments_bp.route("/", methods=["POST"])
@admin_only
def create_department():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"message": "Name is required"}), 400

    if Department.query.filter_by(name=name).first():
        return jsonify({"message": "Department already exists"}), 400

    dept = Department(name=name)
    db.session.add(dept)
    db.session.commit()
    return jsonify({"id": dept.id, "message": "Department created"}), 201

@departments_bp.route("/<int:dept_id>", methods=["PUT"])
@admin_only
def update_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"message": "Name is required"}), 400

    dept.name = name
    db.session.commit()
    return jsonify({"message": "Department updated"}), 200

@departments_bp.route("/<int:dept_id>", methods=["DELETE"])
@admin_only
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify({"message": "Department deleted"}), 200
