from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class OndaTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        access = self.get_token(self.user).access_token
        access["email"] = self.user.email
        access["name"] = self.user.name
        access["nickname"] = self.user.nickname
        access["provider"] = self.user.get_provider_display()
        access["role"] = self.user.get_role_display()

        data["access"] = str(access)
        return data

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)


# 토큰 정보 확인
# https://jwt.io/
