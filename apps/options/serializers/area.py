# apps/options/serializers/area.py
from rest_framework import serializers

from apps.options.models.area import Area


class AreaSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ["id", "area_name", "depth", "children"]

    def get_children(self, obj):
        # 모든 하위 자식을 재귀적으로 직렬화
        children = obj.children.all().order_by("area_name")
        return AreaSerializer(children, many=True).data if children.exists() else []


class AreaWithParentsSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ["id", "area_name", "depth", "parent"]

    def get_parent(self, obj):
        if obj.parent:
            return AreaWithParentsSerializer(obj.parent).data
        return None


class AreaWithFullPathSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ["id", "area_name", "depth", "parent", "full_path"]
