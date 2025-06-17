from django.db import models


class DigitalLevel(models.Model):
    level = models.IntegerField()
    description = models.CharField(max_length=50)

    class Meta:
        ordering = ["level"]
        verbose_name = "디지털 역량 수준"
        verbose_name_plural = "디지털 수준 목록"
        indexes = [models.Index(fields=["level"])]

    def __str__(self):
        return f"{self.level} - {self.description}"
