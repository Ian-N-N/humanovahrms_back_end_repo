from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

def role_required(*roles):
    """
    Example:
    @role_required("Admin")
    @role_required("Admin", "HR")
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.role or user.role.name not in roles:
                return jsonify({"message": "Forbidden"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator

admin_only = role_required("Admin")
hr_only = role_required("Admin", "HR")
employee_only = role_required("Employee")
