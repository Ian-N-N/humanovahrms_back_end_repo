from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    ActivityLogViewSet,
    AttendanceViewSet,
    DepartmentViewSet,
    EmployeeViewSet,
    LeaveRequestViewSet,
    NotificationViewSet,
    PayrollCycleViewSet,
    PayrollViewSet,
    RoleViewSet,
    SettingsView,
    UploadImageView,
    UserViewSet,
)


router = SimpleRouter(trailing_slash=False)
router.register("users", UserViewSet, basename="users")
router.register("employees", EmployeeViewSet, basename="employees")
router.register("departments", DepartmentViewSet, basename="departments")
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("leave", LeaveRequestViewSet, basename="leave")
router.register("payroll/cycles", PayrollCycleViewSet, basename="payroll-cycles")
router.register("payroll", PayrollViewSet, basename="payroll")
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("activity-logs", ActivityLogViewSet, basename="activity-logs")
router.register("roles", RoleViewSet, basename="roles")

urlpatterns = [
    path("upload", UploadImageView.as_view(), name="upload-image"),
    path("upload/", UploadImageView.as_view(), name="upload-image-slash"),
    path("settings", SettingsView.as_view(), name="settings"),
    path("settings/", SettingsView.as_view(), name="settings-slash"),
]
urlpatterns += router.urls
