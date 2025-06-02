from django.db import models

class DigitalLevel(models.Model):
    level = models.IntegerField()
    description = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.level} - {self.description}"
