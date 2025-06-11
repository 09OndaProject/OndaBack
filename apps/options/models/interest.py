from django.db import models


class Interest(models.Model):
    interest_name = models.CharField(max_length=100)  # name -> interest_name

    class Meta:
        ordering = ["id"]
        verbose_name = "관심 분야"
        verbose_name_plural = "관심 분야 목록"
        indexes = [models.Index(fields=["interest_name"])]

    def __str__(self):
        return self.interest_name
