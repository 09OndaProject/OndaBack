from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.options.models.category import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category_name"]

    def validate_category_name(self, value):
        value = value.strip()
        if Category.objects.filter(category_name__iexact=value).exists():
            raise ValidationError("이미 존재하는 카테고리입니다.")
        return value
