from app import ma
from app.models import User, Employee, Department, Role, Attendance, LeaveRequest, Payroll, PayrollCycle, Notification, ActivityLog

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True
    
    manager = ma.Nested('EmployeeSchema', only=['id', 'name'], dump_only=True)
    employee_count = ma.Method("get_employee_count", dump_only=True)
    employees = ma.Nested('EmployeeSchema', many=True, only=['id', 'name', 'job_title', 'status', 'email'], dump_only=True)
    
    def get_employee_count(self, obj):
        return len(obj.employees) if hasattr(obj, 'employees') and obj.employees else 0

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        load_only = ('password_hash',)
    
    role = ma.Nested(RoleSchema)
    # Expose 'username' as 'name' for frontend compatibility
    name = ma.String(attribute='username', dump_only=True)
    employee = ma.Nested('EmployeeSchema', exclude=['user_id'], dump_only=True)

class EmployeeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Employee
        load_instance = True
        include_fk = True
    
    hire_date = ma.Date(format='%Y-%m-%d')
    basic_salary = ma.Decimal(as_string=True)
    leave_balance = ma.Integer()
    created_at = ma.DateTime(format='iso')
    updated_at = ma.DateTime(format='iso')
    personal_email = ma.String()
    profile_photo_url = ma.String()
    name = ma.Method("get_name", dump_only=True)
    department_name = ma.Method("get_department_name", dump_only=True)
    supervisor_name = ma.Method("get_supervisor_name", dump_only=True)
    email = ma.Method("get_email", dump_only=True)

    def get_name(self, obj):
        # Handle cases where first/last might be missing
        fn = getattr(obj, 'first_name', '') or ''
        ln = getattr(obj, 'last_name', '') or ''
        return f"{fn} {ln}".strip() or "Unnamed Employee"

    def get_department_name(self, obj):
        if hasattr(obj, 'department') and obj.department:
            return getattr(obj.department, 'name', None)
        return None

    def get_supervisor_name(self, obj):
        if hasattr(obj, 'supervisor') and obj.supervisor:
            # Check if it's an instance or just the relationship descriptor
            from sqlalchemy.orm.attributes import InstrumentedAttribute
            if not isinstance(obj.supervisor, InstrumentedAttribute):
                fn = getattr(obj.supervisor, 'first_name', '') or ''
                ln = getattr(obj.supervisor, 'last_name', '') or ''
                return f"{fn} {ln}".strip() or "Unnamed Supervisor"
        return None

    def get_email(self, obj):
        if hasattr(obj, 'user') and obj.user:
            return getattr(obj.user, 'email', None)
        return None

class AttendanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attendance
        load_instance = True
        include_fk = True
    
    clock_in_time = ma.Method("get_clock_in_time")
    clock_out_time = ma.Method("get_clock_out_time")
    hours_worked = ma.Float()
    overtime_hours = ma.Float()
    employee = ma.Nested('EmployeeSchema', only=['id', 'name', 'job_title', 'profile_photo_url'], dump_only=True, attribute='attendance_employee')

    def get_clock_in_time(self, obj):
        return obj.clock_in.strftime("%I:%M %p") if obj.clock_in else "--:--"

    def get_clock_out_time(self, obj):
        return obj.clock_out.strftime("%I:%M %p") if obj.clock_out else "--:--"

class LeaveRequestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LeaveRequest
        load_instance = True
        include_fk = True
    
    start_date = ma.Date(format='%Y-%m-%d')
    end_date = ma.Date(format='%Y-%m-%d')
    employee = ma.Nested(EmployeeSchema, only=["id", "name", "job_title"], attribute='leave_employee')
    days = ma.Method("get_days", dump_only=True)
    user_id = ma.Function(lambda obj: obj.leave_employee.user_id if hasattr(obj, 'leave_employee') and obj.leave_employee else None, dump_only=True)

    def get_days(self, obj):
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            return delta.days + 1
        return 0

class PayrollCycleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PayrollCycle
        load_instance = True
        include_fk = True

class PayrollSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payroll
        load_instance = True
        include_fk = True
    
    cycle = ma.Nested(PayrollCycleSchema, dump_only=True)
    employee = ma.Nested(EmployeeSchema, only=["id", "name"], dump_only=True, attribute='payroll_employee')
    basic_salary = ma.Decimal(as_string=True)
    gross_salary = ma.Decimal(as_string=True)
    tax_paid = ma.Decimal(as_string=True)
    nssf = ma.Decimal(as_string=True)
    shif = ma.Decimal(as_string=True)
    housing_levy = ma.Decimal(as_string=True)
    net_salary = ma.Decimal(as_string=True)

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True
        include_fk = True

    # Ensure created_at is serialized as ISO format with Z to indicate UTC
    created_at = ma.Function(lambda obj: obj.created_at.isoformat() + 'Z' if obj.created_at else None)

class ActivityLogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ActivityLog
        load_instance = True
        include_fk = True

    timestamp = ma.Function(lambda obj: obj.timestamp.isoformat() + 'Z' if obj.timestamp else None)
    user_name = ma.Function(lambda obj: obj.user.username if obj.user else 'System')
