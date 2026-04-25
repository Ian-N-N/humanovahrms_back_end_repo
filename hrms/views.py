from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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
from .permissions import (
    EmployeeOwnerOrHr,
    IsAdminRole,
    IsHrOrReadOnly,
    IsHrRole,
    LeaveOwnerOrHr,
    OwnNotification,
    PayrollOwnerOrHr,
    is_admin,
    is_hr,
)
from .serializers import (
    ActivityLogSerializer,
    AttendanceSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    LeaveRequestSerializer,
    NotificationSerializer,
    PayrollCycleSerializer,
    PayrollSerializer,
    RegisterSerializer,
    RoleSerializer,
    SystemSettingSerializer,
    UserSerializer,
)
from .services import calculate_payroll_item
from .uploads import upload_image


class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get("file") or request.FILES.get("image")
        url = upload_image(file_obj)
        return Response({"url": url}, status=status.HTTP_201_CREATED)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if User.objects.exists():
            return Response({"message": "Public admin registration is disabled after bootstrap"}, status=status.HTTP_403_FORBIDDEN)

        role, _ = Role.objects.get_or_create(name="Admin", defaults={"permissions": {}})
        full_name = serializer.validated_data.get("name") or serializer.validated_data.get("username") or "Admin"
        name_parts = full_name.strip().split(" ", 1)
        user = User.objects.create_user(
            email=serializer.validated_data["email"].lower(),
            password=serializer.validated_data["password"],
            username=serializer.validated_data.get("username") or full_name,
            role=role,
        )
        image = serializer.validated_data.get("image")
        Employee.objects.create(
            user=user,
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else "User",
            personal_email=user.email,
            profile_photo_url=upload_image(image) if image else None,
            job_title="System Admin",
            status="Active",
        )
        return Response({"message": "Admin account created successfully"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").lower().strip()
        password = request.data.get("password")
        user = User.objects.filter(email=email).select_related("role", "employee").first()

        if not user or not password or not user.check_password(password):
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"message": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role_name
        access = refresh.access_token
        access["role"] = user.role_name

        return Response(
            {
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    queryset = User.objects.select_related("role", "employee").all().order_by("id")


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [IsAdminRole]
    queryset = Role.objects.all().order_by("name")


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.select_related("manager").prefetch_related("employees").all().order_by("name")

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdminRole()]
        return [IsHrOrReadOnly()]


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Employee.objects.select_related("user", "department", "supervisor").all().order_by("id")

    def get_permissions(self):
        if self.action in {"list", "create", "update", "partial_update", "destroy"}:
            return [IsHrRole()]
        return [IsAuthenticated(), EmployeeOwnerOrHr()]

    def perform_create(self, serializer):
        employee = serializer.save()
        if not employee.employee_number:
            prefix = "GEN"
            if employee.department_id and employee.department.name:
                name = employee.department.name.strip().upper()
                consonants = "".join([char for char in name if char not in "AEIOU "])
                prefix = (consonants[:3] or name[:3] or "GEN")
            employee.employee_number = f"{prefix}-{str(employee.id).zfill(3)}"
            employee.save(update_fields=["employee_number"])

    @action(detail=True, methods=["patch"], url_path="photo", parser_classes=[MultiPartParser, FormParser, JSONParser])
    def photo(self, request, pk=None):
        employee = self.get_object()
        file_obj = request.FILES.get("file") or request.FILES.get("image")
        photo_url = request.data.get("photo_url") or request.data.get("profile_photo_url")
        if file_obj:
            photo_url = upload_image(file_obj)
        if not photo_url:
            return Response({"message": "Provide an image file or photo_url"}, status=status.HTTP_400_BAD_REQUEST)
        employee.profile_photo_url = photo_url
        employee.save(update_fields=["profile_photo_url", "updated_at"])
        return Response(self.get_serializer(employee).data)


class AttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Attendance.objects.select_related("employee").order_by("-date", "-clock_in")
        employee_id = self.request.query_params.get("employee_id")
        if is_hr(self.request.user):
            return queryset.filter(employee_id=employee_id) if employee_id else queryset
        employee = getattr(self.request.user, "employee", None)
        return queryset.filter(employee=employee) if employee else queryset.none()

    @action(detail=False, methods=["post"], url_path="clock-in")
    def clock_in(self, request):
        employee = getattr(request.user, "employee", None)
        if not employee:
            return Response({"message": "Employee record not found"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()
        if Attendance.objects.filter(employee=employee, date=today).exists():
            return Response({"message": "Already clocked in today"}, status=status.HTTP_400_BAD_REQUEST)

        start_setting = SystemSetting.objects.filter(key="shift_start_time").first()
        start_time = datetime.strptime(start_setting.value if start_setting else "09:00", "%H:%M").time()
        grace_limit = timezone.make_aware(datetime.combine(today, start_time)) + timedelta(minutes=15)
        now = timezone.now()
        attendance = Attendance.objects.create(
            employee=employee,
            clock_in=now,
            date=today,
            status=Attendance.STATUS_LATE if now > grace_limit else Attendance.STATUS_ON_TIME,
        )
        ActivityLog.objects.create(user=request.user, action="Clock In", details=f"{employee.name} clocked in")
        return Response(self.get_serializer(attendance).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="clock-out")
    def clock_out(self, request):
        employee = getattr(request.user, "employee", None)
        if not employee:
            return Response({"message": "Employee record not found"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()
        attendance = Attendance.objects.filter(employee=employee, date=today).first()
        if not attendance:
            return Response({"message": "No clock-in record found for today"}, status=status.HTTP_400_BAD_REQUEST)

        attendance.clock_out = timezone.now()
        duration = attendance.clock_out - attendance.clock_in
        attendance.hours_worked = round(duration.total_seconds() / 3600, 2)

        end_setting = SystemSetting.objects.filter(key="shift_end_time").first()
        end_time = datetime.strptime(end_setting.value if end_setting else "17:00", "%H:%M").time()
        shift_end = timezone.make_aware(datetime.combine(today, end_time))
        attendance.overtime_hours = round(max(0, (attendance.clock_out - shift_end).total_seconds()) / 3600, 2)
        attendance.save()
        ActivityLog.objects.create(user=request.user, action="Clock Out", details=f"{employee.name} clocked out")
        return Response(self.get_serializer(attendance).data)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.select_related("employee", "approved_by").all().order_by("-created_at")

    def get_permissions(self):
        if self.action in {"approve", "reject"}:
            return [IsHrRole()]
        if self.action in {"retrieve", "update", "partial_update", "destroy"}:
            return [IsAuthenticated(), LeaveOwnerOrHr()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_hr(self.request.user):
            return queryset
        employee = getattr(self.request.user, "employee", None)
        return queryset.filter(employee=employee) if employee else queryset.none()

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee)

    @action(detail=True, methods=["put"])
    @transaction.atomic
    def approve(self, request, pk=None):
        leave = self.get_object()
        if leave.status != LeaveRequest.STATUS_PENDING:
            return Response({"message": "Only pending leave requests can be approved"}, status=status.HTTP_400_BAD_REQUEST)
        employee = leave.employee
        if employee.leave_balance is not None and employee.leave_balance < leave.days:
            return Response({"message": "Insufficient leave balance"}, status=status.HTTP_400_BAD_REQUEST)
        employee.leave_balance = (employee.leave_balance or 0) - leave.days
        employee.save(update_fields=["leave_balance"])
        leave.status = LeaveRequest.STATUS_APPROVED
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.save(update_fields=["status", "approved_by", "approval_date", "updated_at"])
        if employee.user_id:
            Notification.objects.create(user=employee.user, title="Leave Approved", message="Your leave request has been approved.", type="success")
        return Response(self.get_serializer(leave).data)

    @action(detail=True, methods=["put"])
    def reject(self, request, pk=None):
        leave = self.get_object()
        if leave.status != LeaveRequest.STATUS_PENDING:
            return Response({"message": "Only pending leave requests can be rejected"}, status=status.HTTP_400_BAD_REQUEST)
        leave.status = LeaveRequest.STATUS_REJECTED
        leave.approved_by = request.user
        leave.approval_date = timezone.now()
        leave.save(update_fields=["status", "approved_by", "approval_date", "updated_at"])
        if leave.employee.user_id:
            Notification.objects.create(user=leave.employee.user, title="Leave Rejected", message="Your leave request has been rejected.", type="warning")
        return Response(self.get_serializer(leave).data)

    @action(detail=False, methods=["get"])
    def history(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class PayrollViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollSerializer
    queryset = Payroll.objects.select_related("employee", "cycle").all().order_by("-payment_date")

    def get_permissions(self):
        if self.action in {"retrieve"}:
            return [IsAuthenticated(), PayrollOwnerOrHr()]
        return [IsHrRole()]

    @transaction.atomic
    def create(self, request):
        cycle_id = request.data.get("cycle_id")
        if not cycle_id:
            return Response({"error": "cycle_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        cycle = PayrollCycle.objects.get(pk=cycle_id)
        if cycle.status == "Processed" and Payroll.objects.filter(cycle=cycle).exists():
            return Response({"error": "Payroll cycle has already been processed"}, status=status.HTTP_409_CONFLICT)

        payrolls = []
        for employee in Employee.objects.filter(status="Active"):
            if employee.hire_date and employee.hire_date > cycle.end_date:
                continue
            results = calculate_payroll_item(employee.basic_salary or 0)
            payrolls.append(
                Payroll(
                    employee=employee,
                    cycle=cycle,
                    pay_period_start=cycle.start_date,
                    pay_period_end=cycle.end_date,
                    basic_salary=employee.basic_salary or 0,
                    payment_date=cycle.end_date,
                    status="processed",
                    **results,
                )
            )
        Payroll.objects.bulk_create(payrolls)
        cycle.status = "Processed"
        cycle.save(update_fields=["status"])
        return Response(self.get_serializer(payrolls, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def history(self, request):
        employee = getattr(request.user, "employee", None)
        queryset = self.queryset.filter(employee=employee) if employee else self.queryset.none()
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=["get"])
    def reports(self, request):
        return Response([])


class PayrollCycleViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollCycleSerializer
    permission_classes = [IsHrRole]
    queryset = PayrollCycle.objects.all().order_by("-start_date")


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, OwnNotification]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({setting.key: setting.value for setting in SystemSetting.objects.all()})

    def put(self, request):
        if not is_admin(request.user):
            return Response({"message": "Admins only"}, status=status.HTTP_403_FORBIDDEN)
        updated = []
        for key, value in request.data.items():
            SystemSetting.objects.update_or_create(key=key, defaults={"value": str(value)})
            updated.append(key)
        return Response({"message": "Settings updated successfully", "updated": updated})


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminRole]
    queryset = ActivityLog.objects.select_related("user").order_by("-timestamp")[:50]
