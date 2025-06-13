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
