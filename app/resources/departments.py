from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Department
from app import db
from app.schemas import DepartmentSchema
from app.middleware.auth import admin_required, hr_required
from app.utils.activity_logger import log_activity

department_schema = DepartmentSchema()
department_list_schema = DepartmentSchema(many=True)

class DepartmentList(Resource):
    @jwt_required()
    def get(self):
        departments = Department.query.all()
        return department_list_schema.dump(departments), 200

    @jwt_required()
    @hr_required
    def post(self):
        data = request.get_json()
        
        # Handle manager_id casting (coerce empty string to None)
        manager_id = data.get('manager_id')
        if manager_id == "" or manager_id == "null":
            manager_id = None
        elif manager_id:
            try:
                manager_id = int(manager_id)
            except (ValueError, TypeError):
                return {'message': 'Invalid Manager ID format'}, 400
        
        try:
            new_dept = Department(
                name=data['name'], 
                description=data.get('description'),
                manager_id=manager_id
            )
            db.session.add(new_dept)
            db.session.commit()
            
            # Log Activity
            try:
                user_id = get_jwt_identity()
                log_activity('Department Created', f"Created department '{new_dept.name}'", user_id)
            except:
                pass # Don't fail if log fails? log_activity has try/except usually.
                
            return department_schema.dump(new_dept), 201
        except IntegrityError as e:
            print(f">>> CRITICAL: IntegrityError in Department POST: {str(e)}")
            db.session.rollback()
            if "already exists" in str(e).lower():
                return {'message': f"Department with name '{data['name']}' already exists."}, 400
            return {'message': f"Database integrity error: {str(e)}"}, 400
        except Exception as e:
            print(f">>> CRITICAL: Generic Exception in Department POST: {str(e)}")
            db.session.rollback()
            return {'message': str(e)}, 400

class DepartmentResource(Resource):
    @jwt_required()
    def get(self, id):
        dept = Department.query.get_or_404(id)
        return department_schema.dump(dept), 200

    @jwt_required()
    @hr_required
    def put(self, id):
        dept = Department.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            dept.name = data['name']
        if 'description' in data:
            dept.description = data['description']
        
        if 'manager_id' in data:
            manager_id = data.get('manager_id')
            if manager_id == "" or manager_id == "null":
                dept.manager_id = None
            else:
                try:
                    dept.manager_id = int(manager_id)
                except (ValueError, TypeError):
                    return {'message': 'Invalid Manager ID format'}, 400

        try:
            db.session.commit()
            return department_schema.dump(dept), 200
        except IntegrityError as e:
            db.session.rollback()
            if "already exists" in str(e).lower():
                return {'message': f"Department with name '{data.get('name')}' already exists."}, 400
            return {'message': 'Database integrity error'}, 400
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 400
        
    @jwt_required()
    @admin_required
    def delete(self, id):
        dept = Department.query.get_or_404(id)
        # Check if department has employees
        if dept.employees and len(dept.employees) > 0:
            return {'message': 'Cannot delete department with employees. Reassign or remove employees first.'}, 400
        db.session.delete(dept)
        db.session.commit()
        
        # Log Activity
        try:
             user_id = get_jwt_identity()
             log_activity('Department Deleted', f"Deleted department '{dept.name}'", user_id)
        except:
             pass

        return {'message': 'Department deleted successfully'}, 200
