from flask import request
from flask_restful import Resource
from app.models import Employee, User
from app import db
from app.schemas import EmployeeSchema
from app.middleware.auth import admin_required, hr_required
from flask_jwt_extended import jwt_required

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

class EmployeeList(Resource):
    @jwt_required()
    @hr_required
    def get(self):
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        employees = Employee.query.paginate(page=page, per_page=per_page)
        
        return {
            'employees': employees_schema.dump(employees.items),
            'total': employees.total,
            'pages': employees.pages,
            'current_page': employees.page
        }, 200

    @jwt_required()
    @hr_required
    def post(self):
        data = request.get_json()
        
        # Cast data types correctly
        from datetime import datetime
        hire_date_str = data.get('hire_date') or data.get('join_date')
        hire_date = None
        if hire_date_str:
            try:
                # Handle YYYY-MM-DD
                hire_date = datetime.strptime(hire_date_str.split('T')[0], '%Y-%m-%d').date()
            except (ValueError, IndexError):
                pass

        try:
            basic_salary = float(data.get('basic_salary')) if data.get('basic_salary') else 0.0
        except ValueError:
            basic_salary = 0.0

        mapped_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone_number': data.get('phone_number') or data.get('phone'),
            'profile_photo_url': data.get('profile_photo_url'),
            'department_id': data.get('department_id'),
            'supervisor_id': data.get('supervisor_id'),
            'job_title': data.get('job_title'),
            'basic_salary': basic_salary,
            'hire_date': hire_date,
            'user_id': data.get('user_id')
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        new_employee = Employee(**mapped_data)
        db.session.add(new_employee)
        db.session.commit()
        return employee_schema.dump(new_employee), 201

class EmployeeResource(Resource):
    @jwt_required()
    def get(self, id):
        employee = Employee.query.get_or_404(id)
        return employee_schema.dump(employee), 200

    @jwt_required()
    @hr_required
    def put(self, id):
        employee = Employee.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items():
            setattr(employee, key, value)
        db.session.commit()
        return employee_schema.dump(employee), 200
