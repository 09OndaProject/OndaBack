from rest_framework import serializers
from apps.options.models.digital_level import DigitalLevel

class DigitalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalLevel
        fields = ['id', 'level', 'description']
