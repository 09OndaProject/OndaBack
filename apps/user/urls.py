from django.conf import settings
from django.urls import path

from . import oauth_views_test
from .oauth_views import (
    KakaoCallbackView,
    KakaoLoginRedirectView,
)
from .views import (
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
    # oauth kakao
    path(
        prefix + "/kakao/login",
        KakaoLoginRedirectView.as_view(),
        name="kakao_login",
    ),
    path(
        prefix + "/kakao/callback", KakaoCallbackView.as_view(), name="kakao_callback"
    ),
]

# 개발 환경에서만 test용 OAuth URL 추가
if settings.ENV.get("DJANGO_ENV", "local") == "local":
    urlpatterns += [
        path(
            prefix + "/kakao/login-test",
            oauth_views_test.KakaoLoginRedirectView.as_view(),
            name="kakao_login_test",
        ),
        path(
            prefix + "/kakao/callback-test",
            oauth_views_test.KakaoCallbackView.as_view(),
            name="kakao_callback_test",
        ),
        path(
            prefix + "/oauth/callback-test",
            oauth_views_test.oauth_callback_test_page,
            name="oauth-callback-test",
        ),
    ]
