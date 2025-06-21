from django.conf import settings
from django.urls import path

from apps.user.views import oauth_views_test
from apps.user.views.oauth_views import (
    KakaoCallbackView,
    KakaoLoginRedirectView,
)

app_name = "user_oauth"
prefix = "users"

urlpatterns = [
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
