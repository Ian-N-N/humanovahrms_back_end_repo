from datetime import datetime
from app.extensions import db

class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    job_title = db.Column(db.String(120))
    date_joined = db.Column(db.Date, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    user = db.relationship("User", back_populates="employee")

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    department = db.relationship("Department", back_populates="employees")

    supervisor_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    supervisor = db.relationship("Employee", remote_side=[id])

    def __repr__(self):
        return f"<Employee {self.first_name} {self.last_name}>"
