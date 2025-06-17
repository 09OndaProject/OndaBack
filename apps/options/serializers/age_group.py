from rest_framework import serializers

from apps.options.models.age_group import AgeGroup


class AgeGroupSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()

    class Meta:
        model = AgeGroup
        fields = ["id", "group", "display"]

    def get_display(self, obj):
        return f"{obj.group}대"
