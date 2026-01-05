from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import Employee, LeaveRequest, Attendance, Department
from app.middleware.auth import hr_required
from datetime import date

class DashboardStats(Resource):
    @jwt_required()
    @hr_required
    def get(self):
        total_employees = Employee.query.count()
        today = date.today()
        present_today = Attendance.query.filter_by(date=today, status='present').count()
        pending_leaves = LeaveRequest.query.filter_by(status='pending').count()
        total_departments = Department.query.count()

        return {
            'total_employees': total_employees,
            'present_today': present_today,
            'pending_leaves': pending_leaves,
            'total_departments': total_departments
        }, 200
