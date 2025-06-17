from django.conf import settings
from django.db import models

from apps.upload.models import File

# 자격증 유형 선택지 (라디오 버튼 선택용)
CERTIFICATE_TYPE_CHOICES = [
    ("자격증", "자격증"),
    ("경력증명서", "경력증명서"),
]

# 자격증 유형 선택지 (라디오 버튼 선택용)
CERTIFICATE_TYPE_CHOICES = [
    ("자격증", "자격증"),
    ("경력증명서", "경력증명서"),
]


class LeaderApplicationStatus(models.TextChoices):
    PENDING = "pending", "대기중"
    APPROVED = "approved", "승인됨"
    REJECTED = "rejected", "거절됨"


class LeaderApplication(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leader_application",
        verbose_name="신청자",
    )

    bio = models.TextField(verbose_name="자기소개")
    certificate_type = models.JSONField(verbose_name="자격증 종류")

    # 반복 가능한 활동 사례 (별도 테이블로 구성)
    status = models.CharField(
        max_length=10,
        choices=LeaderApplicationStatus.choices,
        default=LeaderApplicationStatus.PENDING,
        verbose_name="신청 상태",
    )

    reject_reason = models.TextField(null=True, blank=True, verbose_name="거절 사유")

    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="승인일시")

    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="거절일시")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="신청일시")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="처리일시")

    def __str__(self):
        return f"{self.user.nickname or self.user.email}의 리더 신청서"


class LeaderCertificate(models.Model):
    leader_application = models.ForeignKey(
        LeaderApplication,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="리더 신청서",
    )
    certificate_type = models.CharField(
        max_length=30, choices=CERTIFICATE_TYPE_CHOICES, verbose_name="증명서 유형"
    )
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        verbose_name="파일",
    )

    def __str__(self):
        return f"{self.certificate_type} - {self.file.name}"


class PreviousActivity(models.Model):
    leader_application = models.ForeignKey(
        LeaderApplication,
        on_delete=models.CASCADE,
        related_name="previous_activities",
        verbose_name="신청서",
    )

    title = models.CharField(max_length=200, verbose_name="활동 제목")
    description = models.TextField(verbose_name="활동 설명")

    def __str__(self):
        return self.title
