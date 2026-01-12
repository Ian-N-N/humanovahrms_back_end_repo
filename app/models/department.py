from app import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    manager = db.relationship('Employee', foreign_keys=[manager_id], backref='managed_department', lazy=True)

    employees = db.relationship('Employee', foreign_keys='Employee.department_id', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'
