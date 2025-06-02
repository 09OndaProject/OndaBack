from rest_framework import serializers
from apps.options.models.interest import Interest

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']
