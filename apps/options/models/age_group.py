from django.db import models


class AgeGroup(models.Model):
    group = models.IntegerField(help_text="나이대: 10, 20, 30 ...")

    class Meta:
        ordering = ["group"]
        verbose_name = "연령대"
        verbose_name_plural = "연령대 목록"
        indexes = [models.Index(fields=["group"])]

    def __str__(self):
        return f"{self.group}대"
