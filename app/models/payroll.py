from app import db
from datetime import datetime

class PayrollCycle(db.Model):
    __tablename__ = 'payroll_cycles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g. "January 2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active') # Active, Processed, Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    payrolls = db.relationship('Payroll', backref='cycle', lazy=True)

class Payroll(db.Model):
    __tablename__ = 'payroll'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('payroll_cycles.id'), nullable=True)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    gross_salary = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_paid = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    nssf = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shif = db.Column(db.Numeric(10, 2), nullable=False, default=0) # Now SHIF
    housing_levy = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    allowances = db.Column(db.JSON)
    deductions = db.Column(db.JSON)
    net_salary = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending') # pending, processed, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Payroll {self.employee_id} {self.pay_period_start}>'
