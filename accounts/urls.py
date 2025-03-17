from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.views import EmailRegistrationView, PhoneRegistrationView

urlpatterns = [
    path('register/email/', EmailRegistrationView.as_view(), name='register_email'),
    # path('register/phone/', PhoneRegistrationView.as_view(), name='register_phone'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
