from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import Department
from app import db
from app.schemas import DepartmentSchema
from app.middleware.auth import admin_required

department_schema = DepartmentSchema()
department_list_schema = DepartmentSchema(many=True)

class DepartmentList(Resource):
    @jwt_required()
    def get(self):
        departments = Department.query.all()
        return department_list_schema.dump(departments), 200

    @jwt_required()
    @admin_required
    def post(self):
        data = request.get_json()
        new_dept = Department(name=data['name'], description=data.get('description'))
        db.session.add(new_dept)
        db.session.commit()
        return department_schema.dump(new_dept), 201

class DepartmentResource(Resource):
    @jwt_required()
    def get(self, id):
        dept = Department.query.get_or_404(id)
        return department_schema.dump(dept), 200

    @jwt_required()
    @admin_required
    def put(self, id):
        dept = Department.query.get_or_404(id)
        data = request.get_json()
        dept.name = data.get('name', dept.name)
        dept.description = data.get('description', dept.description)
        db.session.commit()
        return department_schema.dump(dept), 200
        
    @jwt_required()
    @admin_required
    def delete(self, id):
        dept = Department.query.get_or_404(id)
        db.session.delete(dept)
        db.session.commit()
        return {'message': 'Department deleted'}, 200
