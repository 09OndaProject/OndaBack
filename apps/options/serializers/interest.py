from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.options.models.interest import Interest


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ["id", "interest_name"]

    def validate_interest_name(self, value):
        value = value.strip()
        if Interest.objects.filter(interest_name__iexact=value).exists():
            raise ValidationError("이미 존재하는 관심사입니다.")
        return value
