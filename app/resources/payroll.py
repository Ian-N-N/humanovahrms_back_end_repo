from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import Payroll, Employee
from app import db
from app.schemas import PayrollSchema
from app.middleware.auth import admin_required

payroll_schema = PayrollSchema()
payroll_list_schema = PayrollSchema(many=True)

class PayrollList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        payrolls = Payroll.query.all()
        return payroll_list_schema.dump(payrolls), 200

    @jwt_required()
    @admin_required
    def post(self):
        # Placeholder for complex payroll generation logic
        # Would typically iterate employees, check attendance, calculate salary
        data = request.get_json()
        new_payroll = Payroll(**data)
        db.session.add(new_payroll)
        db.session.commit()
        return payroll_schema.dump(new_payroll), 201

class PayrollResource(Resource):
    @jwt_required()
    def get(self, id):
        payroll = Payroll.query.get_or_404(id)
        return payroll_schema.dump(payroll), 200
