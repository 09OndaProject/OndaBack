from rest_framework import serializers

from apps.leaders.models import LeaderApplication, LeaderCertificate
from apps.upload.models import File
from apps.upload.serializers import FileSerializer


# 자격증 업로드용 Serializer (쓰기 전용)
# 사용자가 자격증을 업로드할 때 사용됨
# 파일은 File 모델의 PK(id)만 받음
class LeaderCertificateWriteSerializer(serializers.ModelSerializer):
    file = serializers.PrimaryKeyRelatedField(
        queryset=File.objects.all()
    )  # 파일의 ID만 입력 받음

    class Meta:
        model = LeaderCertificate
        fields = ["certificate_type", "file"]  # 자격증 유형과 파일 ID


# 자격증 조회용 Serializer (읽기 전용)
# 관리자 또는 사용자가 자격증 상세정보를 볼 때 사용
# 파일 정보를 FileSerializer 전체로 반환함
class LeaderCertificateReadSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()  # 파일 전체 정보 반환 (이름, 크기, 썸네일 등)

    class Meta:
        model = LeaderCertificate
        fields = ["certificate_type", "file_url"]  # 자격증 유형 + 파일 정보 전체

    def get_file_url(self, obj):
        # 파일이 존재하면 URL 반환, 없으면 None
        if obj.file and obj.file.file:
            return obj.file.file.url
        return None

# 리더 신청 생성 Serializer
# 사용자가 리더 신청서를 보낼 때 사용
# 자격증(certificates)은 여러 개 받을 수 있음
class LeaderApplicationCreateSerializer(serializers.ModelSerializer):
    certificates = LeaderCertificateWriteSerializer(
        many=True
    )  # 자격증 여러 개 입력 가능

    class Meta:
        model = LeaderApplication
        fields = ["id", "bio", "certificate_type", "certificates"]  # 기본 입력 필드
        read_only_fields = ["id"]  # id는 자동 생성되므로 읽기 전용

    def validate(self, data):
        # certificate_type 필수 검사
        if not data.get("certificate_type"):
            raise serializers.ValidationError(
                {"certificate_type": "자격증 종류를 선택해주세요."}
            )
        return data

    def create(self, validated_data):
        # 자격증 데이터만 꺼내서 따로 처리
        certificates_data = validated_data.pop("certificates")

        # LeaderApplication 먼저 생성
        application = LeaderApplication.objects.create(**validated_data)

        # 각 자격증을 LeaderCertificate에 저장 (leader_application 연결)
        for cert in certificates_data:
            LeaderCertificate.objects.create(leader_application=application, **cert)

        return application


# 관리자용 리더 신청 목록 Serializer
# 신청한 사용자 정보와 신청 상태 확인용 (리스트)
# 사용자의 이메일, 이름, 폰번호를 함께 보여줌
class LeaderApplicationListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_phone = serializers.CharField(source="user.phone_number", read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "user_email",
            "user_name",
            "status",
            "created_at",
            "updated_at",
            "user_phone",
        ]


# 리더 신청 상세 조회 Serializer
# 한 명의 신청서 전체 내용을 보여줄 때 사용
# 자격증 정보도 포함 (읽기 전용)
class LeaderApplicationDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_phone = serializers.CharField(source="user.phone_number", read_only=True)
    certificates = LeaderCertificateReadSerializer(
        many=True, read_only=True
    )  # 첨부된 자격증 전체 표시
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = LeaderApplication
        fields = [
            "id",
            "user_email",
            "user_name",
            "user_phone",
            "bio",
            "certificate_type",
            "certificates",
            "status",
            "created_at",
            "updated_at",
        ]


# 리더 신청 상태 변경 Serializer
# 관리자가 승인/거절 처리를 할 때 사용
class LeaderApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderApplication
        fields = ["status"]  # 상태만 변경 가능

    def validate_status(self, value):
        # status 값이 유효한지 검사
        if value not in ["approved", "rejected"]:
            raise serializers.ValidationError(
                "status는 'approved' 또는 'rejected'만 가능합니다."
            )
        return value
