from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import (
    ActivityLog,
    Attendance,
    Department,
    Employee,
    LeaveRequest,
    Notification,
    Payroll,
    PayrollCycle,
    Role,
    SystemSetting,
    User,
)
from .uploads import upload_image


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "permissions", "created_at", "updated_at")


class EmployeeSummarySerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "name", "job_title", "status", "profile_photo_url")


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source="role", write_only=True, required=False)
    employee = EmployeeSummarySerializer(read_only=True)
    name = serializers.CharField(source="username", read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "name", "role", "role_id", "is_active", "employee", "created_at", "updated_at")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    image = serializers.FileField(write_only=True, required=False)

    def validate_password(self, value):
        validate_password(value)
        return value


class DepartmentSerializer(serializers.ModelSerializer):
    manager = EmployeeSummarySerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="manager", write_only=True, required=False, allow_null=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ("id", "name", "description", "manager", "manager_id", "employee_count", "created_at", "updated_at")

    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    image = serializers.FileField(write_only=True, required=False)
    photo_url = serializers.URLField(source="profile_photo_url", write_only=True, required=False, allow_blank=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), source="department", write_only=True, required=False, allow_null=True)
    supervisor_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="supervisor", write_only=True, required=False, allow_null=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "employee_number",
            "user",
            "first_name",
            "last_name",
            "name",
            "phone_number",
            "personal_email",
            "profile_photo_url",
            "photo_url",
            "image",
            "department",
            "department_id",
            "department_name",
            "supervisor",
            "supervisor_id",
            "supervisor_name",
            "job_title",
            "basic_salary",
            "hire_date",
            "status",
            "leave_balance",
            "email",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        if image:
            validated_data["profile_photo_url"] = upload_image(image)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        if image:
            validated_data["profile_photo_url"] = upload_image(image)
        return super().update(instance, validated_data)


class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSummarySerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True, required=False)
    clock_in_time = serializers.SerializerMethodField()
    clock_out_time = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = (
            "id",
            "employee",
            "employee_id",
            "clock_in",
            "clock_out",
            "date",
            "hours_worked",
            "overtime_hours",
            "status",
            "notes",
            "clock_in_time",
            "clock_out_time",
            "created_at",
            "updated_at",
        )

    def get_clock_in_time(self, obj):
        return obj.clock_in.strftime("%I:%M %p") if obj.clock_in else "--:--"

    def get_clock_out_time(self, obj):
        return obj.clock_out.strftime("%I:%M %p") if obj.clock_out else "--:--"


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSummarySerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source="employee", write_only=True, required=False)
    days = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(source="employee.user_id", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = (
            "id",
            "employee",
            "employee_id",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "approved_by",
            "approval_date",
            "days",
            "user_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "approved_by", "approval_date")

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("end_date must be on or after start_date")
        return attrs


class PayrollCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCycle
        fields = ("id", "name", "start_date", "end_date", "status", "created_at")


class PayrollSerializer(serializers.ModelSerializer):
    employee = EmployeeSummarySerializer(read_only=True)
    cycle = PayrollCycleSerializer(read_only=True)

    class Meta:
        model = Payroll
        fields = (
            "id",
            "employee",
            "cycle",
            "pay_period_start",
            "pay_period_end",
            "basic_salary",
            "gross_salary",
            "tax_paid",
            "nssf",
            "shif",
            "housing_levy",
            "allowances",
            "deductions",
            "net_salary",
            "payment_date",
            "status",
            "created_at",
            "updated_at",
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "user", "title", "message", "type", "is_read", "created_at")
        read_only_fields = ("user",)


class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = ("id", "key", "value", "description", "updated_at")


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ActivityLog
        fields = ("id", "user", "user_name", "action", "details", "timestamp")
