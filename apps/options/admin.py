from django.contrib import admin
from apps.options.models import (
    Area, AgeGroup, Interest, DigitalLevel, Category
)

admin.site.register([Area, AgeGroup, Interest, DigitalLevel, Category])
