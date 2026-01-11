from app import ma
from app.models import User, Employee, Department, Role, Attendance, LeaveRequest, Payroll, Notification

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        load_only = ('password_hash',)
    
    role = ma.Nested(RoleSchema)
    # Expose 'username' as 'name' for frontend compatibility
    name = ma.String(attribute='username', dump_only=True)

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True
        include_fk = True

class AttendanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attendance
        load_instance = True
        include_fk = True

class LeaveRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LeaveRequest
        load_instance = True
        include_fk = True

class PayrollSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payroll
        load_instance = True
        include_fk = True

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True
        include_fk = True
