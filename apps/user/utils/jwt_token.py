from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    # access token에만 정보 추가
    access = refresh.access_token
    access["email"] = user.email
    access["name"] = user.name
    access["nickname"] = user.nickname
    access["provider"] = user.get_provider_display()
    access["role"] = user.get_role_display()

    return str(refresh), str(access)


def modify_access_token(access):
    access = AccessToken(access)  # AccessToken 객체로 파싱 (디코딩 + 서명 검증 포함)
    user = User.objects.only("email", "name", "nickname", "provider", "role").get(
        pk=access["user_id"]
    )  # 유저 정보 조회

    # access token에만 정보 추가
    access["email"] = user.email
    access["name"] = user.name
    access["nickname"] = user.nickname
    access["provider"] = user.get_provider_display()
    access["role"] = user.get_role_display()

    return str(access)


def set_refresh_token_cookie(response, refresh_token, request):
    is_prod = settings.DJANGO_ENV == "prod" and request.scheme == "https"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # 백엔드만 접근 가능한 쿠키
        # False: 로컬 개발 환경에 맞춰서 설정 True: HTTPS 환경에서만 전송
        secure=is_prod,
        # samesite="Lax",  # CSRF 공격 방지 설정
        samesite="None",  # CSRF 공격 방지 설정
        path="/api/users/token",  # 필요한 경로에만 쿠키 사용
        domain=(
            "api.ondamoim.com" if is_prod else "127.0.0.1"
        ),  # 특정 도메인에만 쿠키 사용
        max_age=60 * 60 * 24 * 1,  # 1일 (초 단위)
    )
    return response
