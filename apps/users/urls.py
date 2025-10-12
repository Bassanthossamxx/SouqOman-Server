from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    UserDetailView,
    TokenObtainPairThrottledView,
    TokenRefreshThrottledView,
    SendOTPView,
    VerifyOTPView,
    AkedlyCallbackView,
)

urlpatterns = [
    # --- OTP endpoints ---
    path("send/otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify/otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("akedly/callback/", AkedlyCallbackView.as_view(), name="akedly-callback"),

    # --- Auth ---
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserDetailView.as_view(), name="user-detail"),

    # --- JWT tokens ---
    path("token/", TokenObtainPairThrottledView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshThrottledView.as_view(), name="token_refresh"),
]
