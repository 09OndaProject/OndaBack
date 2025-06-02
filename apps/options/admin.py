from django.contrib import admin

from apps.options.models import AgeGroup, Area, Category, DigitalLevel, Interest

admin.site.register([Area, AgeGroup, Interest, DigitalLevel, Category])
