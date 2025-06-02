from django.db import models


class AgeGroup(models.Model):
    group = models.IntegerField(help_text="나이대: 10, 20, 30 ...")

    def __str__(self):
        return f"{self.group}대"
