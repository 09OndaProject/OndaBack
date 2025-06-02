from rest_framework import serializers
from apps.options.models.age_group import AgeGroup

class AgeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroup
        fields = ['id', 'group']
