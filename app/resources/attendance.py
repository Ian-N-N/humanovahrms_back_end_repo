from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Attendance, Employee
from app import db
from app.schemas import AttendanceSchema
from datetime import datetime, date

attendance_schema = AttendanceSchema()
attendance_list_schema = AttendanceSchema(many=True)

class AttendanceList(Resource):
    @jwt_required()
    def get(self):
        # Admin sees all, Employee sees own
        # Simplified for now: return all for testing or filter by emp_id in args
        employee_id = request.args.get('employee_id')
        if employee_id:
            records = Attendance.query.filter_by(employee_id=employee_id).all()
        else:
            records = Attendance.query.all()
        return attendance_list_schema.dump(records), 200

class ClockIn(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return {'message': 'Employee record not found'}, 404
            
        # Check if already clocked in today
        today = date.today()
        existing = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
        if existing:
             return {'message': 'Already clocked in today'}, 400

        attendance = Attendance(
            employee_id=employee.id,
            clock_in=datetime.utcnow(),
            date=today,
            status='present' # Logic to determine late/present
        )
        db.session.add(attendance)
        db.session.commit()
        return attendance_schema.dump(attendance), 201

class ClockOut(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return {'message': 'Employee record not found'}, 404
            
        today = date.today()
        attendance = Attendance.query.filter_by(employee_id=employee.id, date=today).first()
        if not attendance:
             return {'message': 'No clock-in record found for today'}, 400
        
        attendance.clock_out = datetime.utcnow()
        db.session.commit()
        return attendance_schema.dump(attendance), 200
