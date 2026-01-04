from flask import Blueprint, request, jsonify
from app.models import db, User, Employee, Department, Role
from app.rbac import admin_only, hr_only
from app.utils.security import hash_password

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["GET"])
@hr_only
def list_employees():
    employees = Employee.query.all()
    data = [
        {
            "id": e.id,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "job_title": e.job_title,
            "department": e.department.name if e.department else None,
            "user_email": e.user.email,
            "role": e.user.role.name if e.user and e.user.role else None,
            "supervisor_id": e.supervisor_id,
        }
        for e in employees
    ]
    return jsonify(data), 200

@users_bp.route("/", methods=["POST"])
@admin_only
def create_employee_and_user():
    """
    Admin-only:
    - Create User (email, password, role)
    - Create Employee profile
    - Assign department & supervisor
    """
    data = request.get_json() or {}
    required = ["email", "password", "role_id", "first_name", "last_name"]
    if any(field not in data for field in required):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already in use"}), 400

    role = Role.query.get(data["role_id"])
    if not role:
        return jsonify({"message": "Role not found"}), 404

    user = User(
        email=data["email"],
        password_hash=hash_password(data["password"]),
        role_id=role.id,
    )

    dept = None
    if "department_id" in data:
        dept = Department.query.get(data["department_id"])
        if not dept:
            return jsonify({"message": "Department not found"}), 404

    employee = Employee(
        user=user,
        first_name=data["first_name"],
        last_name=data["last_name"],
        job_title=data.get("job_title"),
        department=dept,
        supervisor_id=data.get("supervisor_id"),
    )

    db.session.add(user)
    db.session.add(employee)
    db.session.commit()

    return jsonify(
        {
            "id": employee.id,
            "message": "Employee & user created",
        }
    ), 201

@users_bp.route("/<int:employee_id>", methods=["GET"])
@hr_only
def get_employee(employee_id):
    e = Employee.query.get_or_404(employee_id)
    return jsonify(
        {
            "id": e.id,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "job_title": e.job_title,
            "department_id": e.department_id,
            "user_id": e.user_id,
            "supervisor_id": e.supervisor_id,
        }
    ), 200

@users_bp.route("/<int:employee_id>", methods=["PUT"])
@admin_only
def update_employee(employee_id):
    e = Employee.query.get_or_404(employee_id)
    data = request.get_json() or {}

    for field in ["first_name", "last_name", "job_title"]:
        if field in data:
            setattr(e, field, data[field])

    if "department_id" in data:
        dept = Department.query.get(data["department_id"])
        if not dept:
            return jsonify({"message": "Department not found"}), 404
        e.department = dept

    if "supervisor_id" in data:
        e.supervisor_id = data["supervisor_id"]

    # Optional: allow role change
    if "role_id" in data and e.user:
        role = Role.query.get(data["role_id"])
        if not role:
            return jsonify({"message": "Role not found"}), 404
        e.user.role_id = role.id

    db.session.commit()
    return jsonify({"message": "Employee updated"}), 200

@users_bp.route("/<int:employee_id>/activate", methods=["PATCH"])
@admin_only
def activate_employee(employee_id):
    e = Employee.query.get_or_404(employee_id)
    if e.user:
        e.user.is_active = True
        db.session.commit()
    return jsonify({"message": "Employee activated"}), 200

@users_bp.route("/<int:employee_id>/deactivate", methods=["PATCH"])
@admin_only
def deactivate_employee(employee_id):
    e = Employee.query.get_or_404(employee_id)
    if e.user:
        e.user.is_active = False
        db.session.commit()
    return jsonify({"message": "Employee deactivated"}), 200

@users_bp.route("/<int:employee_id>", methods=["DELETE"])
@admin_only
def delete_employee(employee_id):
    e = Employee.query.get_or_404(employee_id)
    if e.user:
        e.user.is_active = False
    db.session.delete(e)
    db.session.commit()
    return jsonify({"message": "Employee deleted"}), 200
