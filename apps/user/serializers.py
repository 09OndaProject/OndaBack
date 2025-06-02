import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UsernameSerializer(serializers.ModelSerializer):
    """사용자 이름 시리얼라이저"""

    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    # area = AreaSerializer()
    # interest = InterestSerializer()
    # digital_level = DigitalLevelSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "password_confirm",
            "name",
            "nickname",
            "phone_number",
            "date_of_birth",
            # "age_group",
            # "area",
            # "interest",
            # "digital_level",
            # "image_url",
            # "created_at",
            # "updated_at",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {"write_only": True},
            "password": {"write_only": True},
            "password_confirm": {"write_only": True},
            "name": {"write_only": True},
            "nickname": {"write_only": True},
            "phone_number": {"write_only": True},
            "date_of_birth": {"write_only": True},
        }

    # 데이터 검증
    def validate(self, data):
        # 비밀번호 일치 여부 확인
        if data["password"] != data["password_confirm"]:
            raise ValidationError({"detail": "비밀번호가 일치하지 않습니다."})
        data.pop("password_confirm")  # 모델에 없는 필드 제거

        validate_strong_password(data["password"], User(**data))

        data["phone_number"] = validate_phone_number(data["phone_number"])

        return super().validate(data)

    def create(self, validated_data):
        # create_user() -> 비밀번호 해싱
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            nickname=validated_data["nickname"],
            phone_number=validated_data["phone_number"],
            date_of_birth=validated_data["date_of_birth"],
            # area=validated_data["area"],
            # interest=validated_data["interest"],
            # digital_level=validated_data["digital_level"],
        )
        return user


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh_token"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)  # 토큰이 유효한지 검사됨
            print(f"토큰 타입: {token.get('token_type')}")  # 디코드된 토큰 타입 확인
            token.blacklist()  # 블랙리스트 등록
        except Exception:
            raise ValidationError({"detail": "유효하지 않은 리프레시 토큰입니다."})


class UserListSerializer(serializers.ModelSerializer):
    # age_group = serializers.CharField(source="age_group.name", read_only=True)
    # area = serializers.CharField(source="area.name", read_only=True)
    # interest = serializers.CharField(source="interest.name", read_only=True)
    # digital_level = serializers.CharField(source="digital_level.name", read_only=True)
    # digital_level = serializers.CharField(source="digital_level.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "phone_number",
            "date_of_birth",
            # "age_group",
            # "area",
            # "interest",
            # "digital_level",
            # "image_url",
            "created_at",
            "updated_at",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    # area = AreaSerializer()
    # interest = InterestSerializer()
    # digital_level = DigitalLevelSerializer()
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "nickname",
            "phone_number",
            "date_of_birth",
            # "age_group",
            # "area",
            # "interest",
            # "digital_level",
            # "image_url",
            "created_at",
            "updated_at",
        ]

    # serializer.data 출력 값 변환
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("phone_number"):
            data["phone_number"] = format_phone(data["phone_number"])
        return data

    # def get_image_url(self, obj):
    #     profile_image = obj.profile_images.first()
    #     if profile_image and profile_image.file:
    #         # image는 ImageField이기 때문에 .url 속성을 호출하면 저장된 파일의 경로가 자동으로 완전한 URL을 반환
    #         return profile_image.file.url
    #     return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    # password_confirm = serializers.CharField(write_only=True)
    # area = AreaSerializer()
    # interest = InterestSerializer()
    # digital_level = DigitalLevelSerializer()
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            # "password_confirm",
            "name",
            "nickname",
            "phone_number",
            "date_of_birth",
            # "age_group",
            # "area",
            # "interest",
            # "digital_level",
            # "image_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            # write_only : 쓰기만 되고 읽어 오진 않음.
            "password": {"write_only": True}
        }

    # serializer.data 출력 값 변환
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("phone_number"):
            data["phone_number"] = format_phone(data["phone_number"])
        return data

    def validate(self, data):
        # # 비밀번호 일치 여부 확인
        # if data["password"] != data["password_confirm"]:
        #     raise ValidationError({"detail": "비밀번호가 일치하지 않습니다."})
        # data.pop("password_confirm")  # 모델에 없는 필드 제거

        validate_strong_password(data["password"], User(**data))

        if "phone_number" in data and data["phone_number"]:
            data["phone_number"] = validate_phone_number(data["phone_number"])

        return super().validate(data)

    def update(self, instance, validated_data):
        if password := validated_data.get("password"):
            validated_data["password"] = make_password(password)

        return super().update(instance, validated_data)


class PasswordCheckSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


def validate_strong_password(password, user=None):
    try:
        validate_password(password=password, user=user)
    except ValidationError as e:
        raise ValidationError(
            {
                "detail": "비밀번호가 보안 기준을 만족하지 않습니다.",
                "error_message": list(e.messages),
            }
        )


def validate_phone_number(value):
    cleaned = re.sub(r"\D", "", value)
    if not cleaned.isdigit() or len(cleaned) < 11:
        raise serializers.ValidationError("올바른 전화번호를 입력하세요.")
    return cleaned


def format_phone(phone):
    return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
