from rest_framework import serializers

from apps.options.models.area import Area


class AreaSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ["id", "name", "depth", "children"]

    def get_children(self, obj):
        if obj.children.exists():
            return AreaSerializer(obj.children.all(), many=True).data
        return []
