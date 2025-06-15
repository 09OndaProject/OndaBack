# oauth_mixins.py
from django.conf import settings

from apps.user.models import Provider


# 카카오
class KaKaoProviderInfoMixin:
    def get_provider_info(self):
        return {
            "name": "카카오",
            "provider": Provider.KAKAO,
            "callback_url": "/users/kakao/callback",
            "callback_url_test": "/api/users/kakao/callback-test",
            "token_url": "https://kauth.kakao.com/oauth/token",
            "profile_url": "https://kapi.kakao.com/v2/user/me",
            "login_url": "https://kauth.kakao.com/oauth/authorize",
            "state": "kakao_onda",
            "client_id": settings.KAKAO_REST_API_KEY,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
            "email_field": "email",
            "name_field": "name",
            "nickname_field": "nickname",
            "profile_image_field": "profile_image_url",
            "authorization_url": "https://kauth.kakao.com/oauth/authorize",
        }


# 구글
class GoogleProviderInfoMixin:
    def get_provider_info(self):
        return {
            "name": "구글",
            "provider": Provider.GOOGLE,
            "callback_url": "/users/google/callback",
            "callback_url_test": "/api/users/google/callback-test",
            "token_url": "https://oauth2.googleapis.com/token",
            "profile_url": "https://www.googleapis.com/oauth2/v1/userinfo",
            "login_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "state": "google_onda",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "email_field": "email",
            "name_field": "name",
            "nickname_field": "nickname",
            "profile_image_field": "picture",
            "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        }


# 네이버
class NaverProviderInfoMixin:
    def get_provider_info(self):
        return {
            "name": "네이버",
            "provider": Provider.NAVER,
            "callback_url": "/users/naver/callback",
            "callback_url_test": "/api/users/naver/callback-test",
            "token_url": "https://nid.naver.com/oauth2.0/token",
            "profile_url": "https://openapi.naver.com/v1/nid/me",
            "login_url": "https://nid.naver.com/oauth2.0/authorize",
            "state": "naver_onda",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "email_field": "email",
            "name_field": "name",
            "nickname_field": "nickname",
            "profile_image_field": "profile_image",
            "authorization_url": "https://nid.naver.com/oauth2.0/authorize",
        }
