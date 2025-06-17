from rest_framework import serializers

from apps.options.models.area import Area


# 깊이 없이 간단한 구조 (depth 기반 필터링용)
class AreaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "area_name", "depth"]


# 깊이 제한을 고려한 재귀 구조 (자식 포함 구조, 최대 2단계까지)
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
            children, many=True, context={"depth": current_depth + 1}
        ).data


# 상위 부모까지 포함된 구조
class AreaWithParentsSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ["id", "area_name", "depth", "parent"]

    def get_parent(self, obj):
        if obj.parent:
            return AreaWithParentsSerializer(obj.parent).data
        return None


# 전체 경로 포함된 단순 구조
class AreaWithFullPathSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ["id", "area_name", "depth", "parent", "full_path"]
