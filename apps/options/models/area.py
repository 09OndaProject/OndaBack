from django.db import models


class Area(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    depth = models.CharField(max_length=10, help_text="시, 구, 동 등")

    def __str__(self):
        return self.name
