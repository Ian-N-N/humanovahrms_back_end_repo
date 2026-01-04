from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.models import User
from app.utils.security import verify_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=email, is_active=True).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.name,
            },
        }
    ), 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access = create_access_token(identity=user_id, fresh=False)
    return jsonify({"access_token": new_access}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Frontend should delete tokens; blacklist support can be added later
    return jsonify({"message": "Logged out"}), 200
