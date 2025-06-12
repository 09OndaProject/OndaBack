from rest_framework import serializers
from apps.upload.models import File

from apps.leaders.models import (
    LeaderApplication,
    PreviousActivity,
    LeaderCertificate,
)


# 활동 이력 Serializer
class PreviousActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PreviousActivity
        fields = ["title", "description"] #활동 제목 , 설명

# 자격증 업로드 Serializer
class LeaderCertificateSerializer(serializers.ModelSerializer):
    # 업로드된 파일 객체의 PK를 입력 받음
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())

    class Meta:
        model = LeaderCertificate
        fields = ["certificate_type", "file"] # 증명서 유형 + 파일

# 리더 신청 생성 (일반 사용자)
class LeaderApplicationCreateSerializer(serializers.ModelSerializer):
    previous_activities = PreviousActivitySerializer(many=True) # 활동 이력 리스트
    certificates = LeaderCertificateSerializer(many=True) # 자격증 파일 리스트

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "bio",
            "certificate_type",
            "certificates",
            "previous_activities",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        # 필수 항복인 certificate_type
        if not data.get("certificate_type"):
            raise serializers.ValidationError(
                {"certificate_type": "자격증 종류를 선택해주세요."}
            )
        return data

    def create(self, validated_data):
        # certificates / activities 를 분리해서 생성
        certificates_data = validated_data.pop("certificates")
        activities_data = validated_data.pop("previous_activities")

        # LeaderApplication 객체 생성
        application = LeaderApplication.objects.create(**validated_data)

        # 자격증 파일 저장
        for cert in certificates_data:
            LeaderCertificate.objects.create(
                leader_application=application, **cert
            )

        # 활동 이력 저장
        for activity in activities_data:
            PreviousActivity.objects.create(
                leader_application=application, **activity
            )

        return application


# 리더 신청 목록 (관리자)
class LeaderApplicationListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "user_email",
            "user_name",
            "status",
            "created_at",
        ]


# 리더 신청 상세 조회 (관리자 또는 본인)
class LeaderApplicationDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    previous_activities = PreviousActivitySerializer(many=True, read_only=True)
    certificates = LeaderCertificateSerializer(many=True, read_only=True)

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "user_email",
            "user_name",
            "bio",
            "certificate_type",
            "certificates",
            "previous_activities",
            "status",
            "created_at",
        ]


# 승인/거절 처리 (관리자)
class LeaderApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderApplication
        fields = ["status"]

    def validate_status(self, value):
        # 허용된 값인지 검증
        if value not in ["approved", "rejected"]:
            raise serializers.ValidationError(
                "status는 'approved' 또는 'rejected'만 가능합니다."
            )
        return value
