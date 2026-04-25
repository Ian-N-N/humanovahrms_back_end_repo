from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from hrms.views import LoginView, RegisterView


urlpatterns = [
    path("api/auth/register", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login", LoginView.as_view(), name="auth-login"),
    path("api/auth/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/", include("hrms.urls")),
]
