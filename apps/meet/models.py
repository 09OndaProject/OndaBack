# meet/models.py
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from apps.options.models import *
from apps.upload.models import File
from utils.models import TimestampModel

# from apps.file.models import *
User = get_user_model()

class MeetContact(models.TextChoices):
    ONLINE = "on-line", "온라인"
    OFFLINE = "off-line", "오프라인"
    ONOFFLINE = "on/off-line", "온/오프라인"


class Meet(TimestampModel):
    @property
    def status(self):
        now = timezone.now()
        if self.application_deadline and self.application_deadline < now:
            return "마감"
        if self.max_people is not None and self.current_people >= self.max_people:
            return "마감"
        return "모집중"

    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="리더")
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True,verbose_name="지역")
    digital_level = models.ForeignKey(DigitalLevel, on_delete=models.SET_NULL, null=True,verbose_name="디지털난이도")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,verbose_name="카테고리")
    file = models.OneToOneField(File,on_delete=models.CASCADE,verbose_name="대표이미지")
    title = models.CharField(max_length=100,verbose_name="이름")
    description = models.TextField(blank=True, null=True, verbose_name="소개")
    date = models.DateField(null=True, blank=True, verbose_name="일정")
    start_time = models.TimeField(null=True, blank=True, verbose_name="시작시간")
    end_time = models.TimeField(null=True, blank=True, verbose_name="끝나는시간")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="상세주소")
    contact = models.CharField(max_length=10,choices=MeetContact.choices,default=MeetContact.ONLINE,verbose_name="진행방법")
    session_count=models.PositiveIntegerField(default=1,verbose_name="모임횟수")
    max_people = models.IntegerField(null=True, blank=True,verbose_name="최대모집인원")
    current_people = models.IntegerField(default=0,verbose_name="현재인원")
    application_deadline = models.DateTimeField(verbose_name="모집마감일")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="수정일")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="생성일")
    is_deleted = models.BooleanField(default=False,verbose_name="삭제요청")
    link = models.URLField(max_length=500,null=True,blank=True,verbose_name="오픈채팅방링크")
    
    def __str__(self):
        return f"[{self.pk}] {self.title}"
    
    class Meta:
        verbose_name = "모임"
        verbose_name_plural = "모임 목록"
        ordering = ["-created_at"]


class MeetApply(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="meet_applies"
    )
    meet = models.ForeignKey(
        Meet, on_delete=models.CASCADE, related_name="applications"
    )
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="가입일자")

    class Meta:
        unique_together = ("user", "meet")

    def __str__(self):
        return f"{self.user.nickname} → {self.meet.title}"


"""
class MeetBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meet_applies')
    meet = models.ForeignKey('Meet', on_delete=models.CASCADE, related_name='applications')
    created_at = models.DateTimeField("생성일자", auto_now_add=True)

    class Meta:
        unique_together = ('user', 'meet')

    def __str__(self):
        return f"{self.user.nickname} → {self.meet.title}"
"""
