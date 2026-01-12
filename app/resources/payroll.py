from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import Payroll, Employee, PayrollCycle
from app import db
from app.schemas import PayrollSchema, PayrollCycleSchema
from app.middleware.auth import admin_required, hr_required
from app.utils.payroll_calculator import calculate_payroll_item
from datetime import datetime

payroll_schema = PayrollSchema()
payroll_list_schema = PayrollSchema(many=True)
cycle_schema = PayrollCycleSchema()
cycle_list_schema = PayrollCycleSchema(many=True)

class PayrollList(Resource):
    @jwt_required()
    @hr_required
    def get(self):
        payrolls = Payroll.query.all()
        return payroll_list_schema.dump(payrolls), 200

    @jwt_required()
    @hr_required
    def post(self):
        """
        Run payroll for a specific cycle.
        Expected JSON: { "cycle_id": 1 }
        """
        data = request.get_json()
        cycle_id = data.get('cycle_id')
        if not cycle_id:
            return {'error': 'cycle_id is required'}, 400
            
        cycle = PayrollCycle.query.get_or_404(cycle_id)
        if cycle.status == 'Processed':
            return {'error': 'Payroll already processed for this cycle'}, 400
            
        # 1. Get all active employees
        employees = Employee.query.filter_by(status='Active').all()
        
        created_payrolls = []
        for emp in employees:
            salary = emp.basic_salary or 0
            # Calculate KES breakdown
            results = calculate_payroll_item(salary)
            
            new_payroll = Payroll(
                employee_id=emp.id,
                cycle_id=cycle.id,
                pay_period_start=cycle.start_date,
                pay_period_end=cycle.end_date,
                basic_salary=salary,
                gross_salary=results['gross_salary'],
                tax_paid=results['tax_paid'],
                nssf=results['nssf'],
                nhif=results['shif'], # Storing SHIF in nhif column
                housing_levy=results['housing_levy'],
                net_salary=results['net_salary'],
                payment_date=datetime.utcnow().date(),
                status='processed'
            )
            db.session.add(new_payroll)
            created_payrolls.append(new_payroll)
            
        # 2. Update cycle status
        cycle.status = 'Processed'
        db.session.commit()
        
        return payroll_list_schema.dump(created_payrolls), 201

class PayrollResource(Resource):
    @jwt_required()
    def get(self, id):
        payroll = Payroll.query.get_or_404(id)
        return payroll_schema.dump(payroll), 200

class PayrollCycles(Resource):
    @jwt_required()
    @hr_required
    def get(self):
        cycles = PayrollCycle.query.all()
        return cycle_list_schema.dump(cycles), 200
        
    @jwt_required()
    @hr_required
    def post(self):
        data = request.get_json()
        try:
            new_cycle = PayrollCycle(
                name=data['name'],
                start_date=data['startDate'], # Frontend uses camelCase
                end_date=data['endDate']
            )
            db.session.add(new_cycle)
            db.session.commit()
            return cycle_schema.dump(new_cycle), 201
        except Exception as e:
            return {'error': str(e)}, 400

class PayrollReports(Resource):
    @jwt_required()
    @hr_required
    def get(self):
        # Placeholder for reports
        return [], 200
