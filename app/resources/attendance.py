from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Attendance, Employee
from app import db
from app.schemas import AttendanceSchema
from datetime import datetime, date, timedelta
from app.utils.activity_logger import log_activity

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

        # Fetch Shift Start Time from Settings (Default to 09:00 if not set)
        from app.models.setting import SystemSetting
        
        setting = SystemSetting.query.filter_by(key='shift_start_time').first()
        start_time_str = setting.value if setting else "09:00"
        
        # Parse start time
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        
        # Add 15 minutes grace period
        # Simple logic: Convert to minutes, add 15, convert back or compare
        # Easier: compare if current time > start time + 15 mins
        
        # We need a robust comparison. Let's use full datetime for today
        shift_start_dt = datetime.combine(today, start_time)
        grace_period_limit = shift_start_dt + timedelta(minutes=15)
        
        current_dt = datetime.now()
        
        status = 'Late' if current_dt > grace_period_limit else 'On Time'

        attendance = Attendance(
            employee_id=employee.id,
            clock_in=current_dt,
            date=today,
            status=status
        )
        db.session.add(attendance)
        db.session.commit()
        
        # Log Activity
        log_activity('Clock In', f"{employee.first_name} {employee.last_name} clocked in ({status})", user_id)
        
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
        
        attendance.clock_out = datetime.now()
        
        # Calculate hours worked
        if attendance.clock_in:
            duration = attendance.clock_out - attendance.clock_in
            attendance.hours_worked = round(duration.total_seconds() / 3600, 2)
            
            # Calculate Overtime
            from app.models.setting import SystemSetting
            setting_end = SystemSetting.query.filter_by(key='shift_end_time').first()
            end_time_str = setting_end.value if setting_end else "17:00"
            shift_end_time = datetime.strptime(end_time_str, "%H:%M").time()
            shift_end_dt = datetime.combine(today, shift_end_time)
            
            if attendance.clock_out > shift_end_dt:
                ot_duration = attendance.clock_out - shift_end_dt
                attendance.overtime_hours = round(ot_duration.total_seconds() / 3600, 2)
            else:
                 attendance.overtime_hours = 0.0
            
        db.session.commit()
        
        # Log Activity
        log_activity('Clock Out', f"{employee.first_name} {employee.last_name} clocked out. Worked: {attendance.hours_worked}hrs", user_id)
        
        return attendance_schema.dump(attendance), 200

class PersonalAttendanceHistory(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return {'message': 'Employee record not found'}, 404
            
        records = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).all()
        return attendance_list_schema.dump(records), 200
