from rest_framework import serializers
from apps.leaders.models import LeaderApplication, PreviousActivity


# 리더 신청 생성 (일반 사용자)
class PreviousActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PreviousActivity
        fields = ["title", "description"]


class LeaderApplicationCreateSerializer(serializers.ModelSerializer):
    previous_activities = PreviousActivitySerializer(many=True)

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "bio",
            "certificate_type",
            "previous_activities",
            # "certificate_upload",  # 이미지 업로드 준비 중
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        if not data.get("certificate_type"):
            raise serializers.ValidationError({"certificate_type": "자격증 종류를 선택해주세요."})
        return data

    def create(self, validated_data):
        activities_data = validated_data.pop("previous_activities")
        application = LeaderApplication.objects.create(**validated_data)
        for activity in activities_data:
            PreviousActivity.objects.create(leader_application=application, **activity)
        return application


# 신청 목록 (관리자)
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


# 신청 상세 조회 (관리자 또는 본인)
class LeaderApplicationDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    previous_activities = PreviousActivitySerializer(many=True, read_only=True)

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "user_email",
            "user_name",
            "bio",
            "certificate_type",
            "previous_activities",
            # "certificate_upload",  # 이미지 업로드 준비 중
            "status",
            "created_at",
        ]


# 승인/거절 처리 (관리자)
class LeaderApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderApplication
        fields = ["status"]

    def validate_status(self, value):
        if value not in ["approved", "rejected"]:
            raise serializers.ValidationError("status는 'approved' 또는 'rejected'만 가능합니다.")
        return value
