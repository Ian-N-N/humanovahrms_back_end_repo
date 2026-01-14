from app import ma
from app.models import User, Employee, Department, Role, Attendance, LeaveRequest, Payroll, PayrollCycle, Notification

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        load_instance = True

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
        include_fk = True
    
    manager = ma.Nested('EmployeeSchema', dump_only=True)

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
    name = ma.Method("get_name", dump_only=True)

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class AttendanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attendance
        load_instance = True
        include_fk = True
    
    clock_in_time = ma.Method("get_clock_in_time")
    clock_in_time = ma.Method("get_clock_in_time")
    clock_out_time = ma.Method("get_clock_out_time")
    hours_worked = ma.Float()

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
    employee = ma.Nested(EmployeeSchema, only=["id", "name", "job_title"])
    days = ma.Method("get_days", dump_only=True)
    user_id = ma.Function(lambda obj: obj.employee.user_id if obj.employee else None, dump_only=True)

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
    employee = ma.Nested(EmployeeSchema, only=["id", "name"], dump_only=True)
    basic_salary = ma.Decimal(as_string=True)
    gross_salary = ma.Decimal(as_string=True)
    tax_paid = ma.Decimal(as_string=True)
    nssf = ma.Decimal(as_string=True)
    nhif = ma.Decimal(as_string=True, attribute='nhif') # Keep attribute name for now
    housing_levy = ma.Decimal(as_string=True)
    net_salary = ma.Decimal(as_string=True)

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True
        include_fk = True
