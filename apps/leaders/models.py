from django.conf import settings
from django.db import models

from apps.upload.models import File  # 업로드된 파일을 저장하는 File 모델 참조

# 자격증 유형 선택지 (리더가 제출할 수 있는 증명서의 종류)
CERTIFICATE_TYPE_CHOICES = [
    ("자격증", "자격증"),
    ("경력증명서", "경력증명서"),
]


# 리더 신청 상태를 나타내는 선택지 (신청 → 승인 or 거절)
class LeaderApplicationStatus(models.TextChoices):
    PENDING = "pending", "대기중"  # 기본값 (관리자 확인 전 상태)
    APPROVED = "approved", "승인됨"  # 관리자가 신청을 승인함
    REJECTED = "rejected", "거절됨"  # 관리자가 신청을 거절함


# 리더 신청서 모델 (한 명의 유저가 리더가 되기 위해 작성하는 신청서)
class LeaderApplication(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # 신청한 사용자
        on_delete=models.CASCADE,  # 유저가 삭제되면 신청서도 함께 삭제
        related_name="leader_application",  # user.leader_application 으로 접근 가능
        verbose_name="신청자",
    )
    bio = models.TextField(verbose_name="자기소개")  # 사용자가 작성한 자기소개
    certificate_type = models.JSONField(
        null=True, blank=True, verbose_name="자격증 종류"
    )  # 여러 자격증 종류 저장 가능 (리스트 형태)

    # 신청 상태 (대기중, 승인됨, 거절됨 중 하나)
    status = models.CharField(
        max_length=10,
        choices=LeaderApplicationStatus.choices,  # 위에서 정의한 선택지 사용
        default=LeaderApplicationStatus.PENDING,  # 기본값은 "대기중"
        verbose_name="신청 상태",
    )

    # 거절 사유 (거절된 경우 관리자가 작성)
    reject_reason = models.TextField(null=True, blank=True, verbose_name="거절 사유")

    # 승인/거절 처리된 시점 저장
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="승인일시")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="거절일시")

    # 생성 및 수정 시간 기록 (자동 설정)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="신청일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="처리일시")

    def __str__(self):
        # 관리자 페이지 등에서 보기 좋게 표시 (닉네임 또는 이메일 기준)
        return f"{self.user.nickname or self.user.email}의 리더 신청서"


# 리더 자격증 모델 (신청서에 첨부된 자격증/경력증명서 정보 저장)
class LeaderCertificate(models.Model):
    leader_application = models.ForeignKey(
        LeaderApplication,  # 어떤 리더 신청서에 연결된 자격증인지
        on_delete=models.CASCADE,  # 신청서가 삭제되면 자격증도 함께 삭제
        related_name="certificates",  # leader_application.certificates 로 접근 가능
        verbose_name="리더 신청서",
    )
    certificate_type = models.CharField(
        max_length=30,
        choices=CERTIFICATE_TYPE_CHOICES,  # "자격증" 또는 "경력증명서"
        verbose_name="증명서 유형",
    )
    file = models.ForeignKey(
        File,  # 실제 파일 저장된 모델 (PDF, 이미지 등)
        on_delete=models.CASCADE,  # 파일이 삭제되면 자격증도 함께 삭제
        verbose_name="파일",
    )

    def __str__(self):
        # 관리자 페이지 등에서 보기 좋게 표시
        return f"{self.certificate_type} - {self.file.file_name}"
