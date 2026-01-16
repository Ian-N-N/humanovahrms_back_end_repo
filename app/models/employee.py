from app import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    personal_email = db.Column(db.String(255))
    profile_photo_url = db.Column(db.String(500))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    job_title = db.Column(db.String(100))
    basic_salary = db.Column(db.Numeric(10, 2))
    hire_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active') 
    leave_balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subordinates = db.relationship('Employee', remote_side=[id], backref='supervisor', lazy=True)
    attendance = db.relationship('Attendance', backref='attendance_employee', lazy=True)
    leave_requests = db.relationship('LeaveRequest', backref='leave_employee', lazy=True)
    payroll_records = db.relationship('Payroll', backref='payroll_employee', lazy=True)

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'
