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
    @admin_required
    def post(self):
        data = request.get_json()
        # Basic validation and creation logic would go here
        # Note: Needs user_id linking logic
        new_employee = Employee(**data)
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
