# meet/models.py
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from options.models import *
User = get_user_model()


class Meet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    digital_level = models.ForeignKey(
        DigitalLevel, on_delete=models.SET_NULL, null=True
    )
    interest = models.ForeignKey(Interest, on_delete=models.SET_NULL, null=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    max_people = models.IntegerField(null=True, blank=True)
    current_people = models.IntegerField(default=0)
    # file = GenericRelation("Image")
    application_deadline = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.pk}] {self.title}"


class MeetApply(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="meet_applies"
    )
    meet = models.ForeignKey(
        "Meet", on_delete=models.CASCADE, related_name="applications"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "meet")

    def __str__(self):
        return f"{self.user.nickname} → {self.meet.title}"


"""
class MeetBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meet_applies')
    meet = models.ForeignKey('Meet', on_delete=models.CASCADE, related_name='applications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'meet')

    def __str__(self):
        return f"{self.user.nickname} → {self.meet.title}"
"""
