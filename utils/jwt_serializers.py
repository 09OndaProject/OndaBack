from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class OndaTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 토큰에 유저 정보를을 함께 담아서 보냄
        token["email"] = user.email
        token["name"] = user.name
        token["nickname"] = user.nickname
        token["provider"] = user.get_provider_display()
        token["role"] = user.get_role_display()

        return token


# 토큰 정보 확인
# https://jwt.io/
