from app import db
from datetime import datetime

class Payroll(db.Model):
    __tablename__ = 'payroll'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    allowances = db.Column(db.JSON)
    deductions = db.Column(db.JSON)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending') # pending, processed, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Payroll {self.employee_id} {self.pay_period_start}>'
