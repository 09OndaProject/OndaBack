from rest_framework import serializers

from apps.options.models.digital_level import DigitalLevel


class DigitalLevelSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()

    class Meta:
        model = DigitalLevel
        fields = ["id", "level", "description", "display"]

    def get_display(self, obj):
        return f"{obj.level} - {obj.description}"
