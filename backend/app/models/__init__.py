from app.extensions import db
from .role import Role
from .department import Department
from .user import User
from .employee import Employee

__all__ = ["db", "Role", "Department", "User", "Employee"]
