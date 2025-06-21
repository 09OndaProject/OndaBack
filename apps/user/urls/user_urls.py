from django.urls import path

from apps.user.views.user_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutAPIView,
    PasswordCheckView,
    ProfileView,
    RegisterView,
    VerifyEmailView,
)

app_name = "user"
prefix = "users"

urlpatterns = [
    # 회원가입
    path(prefix + "/signup", RegisterView.as_view(), name="signup"),
    # 이메일 인증
    path(prefix + "/verify/email", VerifyEmailView.as_view(), name="verify_email"),
    # 비밀번호 확인
    path(
        prefix + "/check/password", PasswordCheckView.as_view(), name="password_check"
    ),
    # 프로필
    path(prefix + "/profile", ProfileView.as_view(), name="profile"),
    # JWT 로그인, 로그아웃, 리프레시
    path(
        prefix + "/token/login", CustomTokenObtainPairView.as_view(), name="token_login"
    ),
    path(prefix + "/token/logout", LogoutAPIView.as_view(), name="token_logout"),
    path(
        prefix + "/token/refresh",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
