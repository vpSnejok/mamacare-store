from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from accounts.views import RegisterView, LoginView, LogoutView, LogoutAllView, ChangePasswordView, \
    DatabaseHealthCheckView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/logout-all/', LogoutAllView.as_view(), name='auth_logout_all'),
    path('auth/password/change/', ChangePasswordView.as_view(), name='auth_password_change'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('health-check/', DatabaseHealthCheckView.as_view(), name='db-health-check'),
]
