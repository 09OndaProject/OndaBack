from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.meet.models import Meet

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE, related_name="reviews")  # ✅ 주석 해제
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField(max_length=500)
    inconvenience = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "meet"]  # ✅ 중복 리뷰 방지용 (선택)

    def __str__(self):
        return f"{self.user} - {self.meet} ({self.rating}점)"  # ✅ 가독성용
