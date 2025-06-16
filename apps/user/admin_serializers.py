import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.options.models import Interest
from apps.options.serializers.area import AreaWithFullPathSerializer
from apps.options.serializers.digital_level import DigitalLevelSerializer
from apps.options.serializers.interest import InterestSerializer
from apps.upload.serializers import FileSerializer

User = get_user_model()


class AdminUserListSerializer(serializers.ModelSerializer):
    # age_group = serializers.CharField(source="age_group.name", read_only=True)
    area = serializers.CharField(source="area.full_path", read_only=True)
    interests = serializers.SlugRelatedField(
        slug_field="interest_name", read_only=True, many=True
    )
    digital_level = serializers.CharField(
        source="digital_level.description", read_only=True
    )
    file = serializers.CharField(source="file.file.url", read_only=True)
    thumbnail = serializers.CharField(source="file.thumbnail.url", read_only=True)

    class Meta:
        model = User
        fields = "__all__"

    # serializer.data 출력 값 변환
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if phone_number := data.get("phone_number"):
            data["phone_number"] = format_phone(phone_number)
        return data


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    interests = serializers.PrimaryKeyRelatedField(
        queryset=Interest.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ["id", "last_login", "created_at", "updated_at"]
        extra_kwargs = {
            "password": {"write_only": True},
            "password_confirm": {"write_only": True},
        }

        if not settings.DEBUG:
            extra_kwargs.update(
                {
                    "email": {"write_only": True},
                    "name": {"write_only": True},
                    "nickname": {"write_only": True},
                    "phone_number": {"write_only": True},
                    "date_of_birth": {"write_only": True},
                    "area": {"write_only": True},
                    "interests": {"write_only": True},
                    "digital_level": {"write_only": True},
                    "file": {"write_only": True},
                }
            )

    # 데이터 검증
    def validate(self, data):
        password = data.get("password")
        password_confirm = data.get("password_confirm")
        phone_number = data.get("phone_number")

        # 비밀번호 일치 여부 확인
        if password_confirm:
            if password != password_confirm:
                raise serializers.ValidationError(
                    {"detail": "비밀번호가 일치하지 않습니다."}
                )
            data.pop("password_confirm")  # 모델에 없는 필드 제거

        if password:
            validate_strong_password(password)

        if phone_number:
            data["phone_number"] = validate_phone_number(phone_number)

        return super().validate(data)

    def create(self, validated_data):
        interests = validated_data.pop("interests", [])

        # create_user 비밀번호 해싱 포함
        user = User.objects.create_user(**validated_data)

        if interests:
            user.interests.set(interests)

        return user

    # serializer.data 출력 값 변환
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if phone_number := data.get("phone_number"):
            data["phone_number"] = format_phone(phone_number)
        return data


class AdminUserProfileSerializer(serializers.ModelSerializer):
    area = AreaWithFullPathSerializer()
    interests = InterestSerializer(many=True, read_only=True)
    digital_level = DigitalLevelSerializer()
    file = FileSerializer()

    class Meta:
        model = User
        exclude = ["password"]
        # exclude = [] : fields = "__all__" 에서 특정 필드 제외
        # fields = "__all__"와 같이 사용 불가

    # serializer.data 출력 값 변환
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if phone_number := data.get("phone_number"):
            data["phone_number"] = format_phone(phone_number)
        return data


class AdminUserProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "is_active", "role"]
        read_only_fields = ["id"]
        if not settings.DEBUG:
            extra_kwargs = {
                # write_only : 쓰기만 되고 읽어 오진 않음.
                "is_active": {"write_only": True},
                "role": {"write_only": True},
            }


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
