from rest_framework import serializers
from apps.options.models.area import Area


# 깊이 없이 간단한 구조
class AreaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "area_name", "depth"]


# 깊이 제한을 고려한 재귀 직렬화
class AreaSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ["id", "area_name", "depth", "children"]

    def get_children(self, obj):
        current_depth = self.context.get("depth", 1)
        if current_depth > 2:
            return []

        children = obj.children.all().order_by("id")
        return AreaSerializer(
            children,
            many=True,
            context={"depth": current_depth + 1}
        ).data if children.exists() else []
