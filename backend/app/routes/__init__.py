# app/routes/__init__.py
from .auth import auth_bp
from .users import users_bp
from .departments import departments_bp
from .upload import upload_bp

__all__ = ["auth_bp", "users_bp", "departments_bp", "upload_bp"]
