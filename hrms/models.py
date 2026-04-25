from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        admin_role, _ = Role.objects.get_or_create(name="Admin", defaults={"permissions": {}})
        extra_fields.setdefault("role", admin_role)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField("password_hash", max_length=255, db_column="password_hash")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"

    @property
    def role_name(self):
        return self.role.name if self.role_id else None

    def __str__(self):
        return self.email


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="managed_departments",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "departments"

    def __str__(self):
        return self.name


class Employee(models.Model):
    employee_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee", blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    personal_email = models.EmailField(max_length=255, blank=True, null=True)
    profile_photo_url = models.URLField(max_length=500, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name="employees", blank=True, null=True)
    supervisor = models.ForeignKey("self", on_delete=models.SET_NULL, related_name="subordinates", blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, default="Active")
    leave_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employees"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.name


class Attendance(models.Model):
    STATUS_ON_TIME = "On Time"
    STATUS_LATE = "Late"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendance")
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(blank=True, null=True)
    date = models.DateField()
    hours_worked = models.FloatField(default=0.0)
    overtime_hours = models.FloatField(default=0.0)
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance"
        constraints = [
            models.UniqueConstraint(fields=["employee", "date"], name="uq_attendance_employee_date"),
        ]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["employee", "date"]),
        ]

    def __str__(self):
        return f"{self.employee_id} {self.date}"


class LeaveRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default=STATUS_PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="approved_leaves")
    approval_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leave_requests"
        indexes = [
            models.Index(fields=["employee", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.employee_id} {self.status}"


class PayrollCycle(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default="Active")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "payroll_cycles"

    def __str__(self):
        return self.name


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="payroll_records")
    cycle = models.ForeignKey(PayrollCycle, on_delete=models.SET_NULL, related_name="payrolls", blank=True, null=True)
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nssf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shif = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    housing_levy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.JSONField(blank=True, null=True)
    deductions = models.JSONField(blank=True, null=True)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payroll"
        constraints = [
            models.UniqueConstraint(fields=["employee", "cycle"], name="uq_payroll_employee_cycle"),
        ]

    def __str__(self):
        return f"{self.employee_id} {self.pay_period_start}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, default="info")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return self.title


class SystemSetting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_settings"

    def __str__(self):
        return f"{self.key}={self.value}"


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="activities", blank=True, null=True)
    action = models.CharField(max_length=50)
    details = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "activity_logs"
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.user_id}"
