from django.db import models


class Area(models.Model):
    area_name = models.CharField(max_length=100)  # 변경된 필드명
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    depth = models.CharField(
        max_length=10, help_text="지역 유형: 시, 구, 동 등"
    )  # 다시 원래 이름 사용

    class Meta:
        ordering = ["area_name"]
        verbose_name = "지역"
        verbose_name_plural = "지역 목록"
        indexes = [models.Index(fields=["depth"])]

    def __str__(self):
        return f"{self.area_name} ({self.depth})"
