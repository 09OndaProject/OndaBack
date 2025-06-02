from django.apps import apps
from rest_framework import serializers

AgeGroup = apps.get_model("option", "AgeGroup")
Area = apps.get_model("option", "Area")
Interest = apps.get_model("option", "Interest")
Digital_level = apps.get_model("option", "Digital_level")
Category = apps.get_model("option", "Category")


class AgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        fields = ("id", "group")


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "name", "parent_id", "depth")


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ("id", "name")


class DigitalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digital_level
        fields = ("id", "level", "description")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ("id", "name")
