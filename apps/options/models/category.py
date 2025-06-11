from django.db import models


class Category(models.Model):
    category_name = models.CharField(
        max_length=50
    )  # 테이블 상 name -> category_name 로 변경

    class Meta:
        ordering = ["id"]
        verbose_name = "카테고리"
        verbose_name_plural = "카테고리 목록"
        indexes = [models.Index(fields=["category_name"])]

    def __str__(self):
        return self.category_name
