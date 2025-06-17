from django.db import models


class Area(models.Model):
    area_name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    depth = models.CharField(max_length=10, help_text="지역 유형: 시, 구, 동 등")

    class Meta:
        ordering = ["id"]
        verbose_name = "지역"
        verbose_name_plural = "지역 목록"
        indexes = [models.Index(fields=["depth"])]

    def __str__(self):
        return f"{self.area_name} ({self.depth})"

    @property
    def full_path(self):
        names = [self.area_name]
        parent = self.parent
        while parent:
            names.append(parent.area_name)
            parent = parent.parent
        return " ".join(reversed(names))
