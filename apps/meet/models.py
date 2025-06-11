# meet/models.py
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.options.models import *
from utils.models import TimestampModel
from django.utils import timezone

# from apps.file.models import *
User = get_user_model()


class Meet(TimestampModel):
    @property
    def status(self):
        if self.application_deadline and self.application_deadline < timezone.now():
            return "마감"
        return "모집중"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    digital_level = models.ForeignKey(
        DigitalLevel, on_delete=models.SET_NULL, null=True
    )
    interest = models.ForeignKey(Interest, on_delete=models.SET_NULL, null=True)
    
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    max_people = models.IntegerField(null=True, blank=True)
    current_people = models.IntegerField(default=0)
    application_deadline = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # file = models.OneToOneField(File,on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.pk}] {self.title}"


class MeetApply(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="meet_applies"
    )
    meet = models.ForeignKey(
        "Meet", on_delete=models.CASCADE, related_name="applications"
    )
    created_at = models.DateTimeField("생성일자", auto_now_add=True)

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
