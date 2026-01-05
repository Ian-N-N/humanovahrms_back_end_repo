from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User
from app.models.role import Role

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')

            if user_role not in roles:
                return jsonify(msg='Admins only!'), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_required(fn):
    return role_required('Admin')(fn)

def hr_required(fn):
    return role_required('Admin', 'HR Manager')(fn)

# Helper to check if user owns resource or is admin/hr
def owner_or_hr_required(model, owner_field='user_id'):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')

            # 1. Allow Admin or HR
            if user_role in ['Admin', 'HR Manager']:
                return fn(*args, **kwargs)

            # 2. Check Ownership
            user_id = get_jwt_identity()
            
            # Determine the comparator ID (User ID vs Employee ID)
            comparator_id = user_id
            if owner_field == 'employee_id':
                from app.models.employee import Employee
                employee = Employee.query.filter_by(user_id=user_id).first()
                if not employee:
                    return jsonify(msg='Employee profile not found'), 404
                comparator_id = employee.id

            # Fetch the resource
            if 'id' in kwargs:
                resource_id = kwargs['id']
                resource = model.query.get(resource_id)
                if not resource:
                    return jsonify(msg='Resource not found'), 404
                
                # Compare
                if getattr(resource, owner_field) != comparator_id:
                     return jsonify(msg='Unauthorized access'), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper
