from rest_framework.views import APIView
from rest_framework.response import Response

from apps.options.models import (
    Category, Area, Interest, DigitalLevel, AgeGroup
)
from apps.options.serializers.category import CategorySerializer
from apps.options.serializers.area import AreaSerializer
from apps.options.serializers.interest import InterestSerializer
from apps.options.serializers.digital_level import DigitalLevelSerializer
from apps.options.serializers.age_group import AgeGroupSerializer


class OptionAllView(APIView):
    def get(self, request):
        return Response({
            "categories": CategorySerializer(Category.objects.all(), many=True).data,
            "areas": AreaSerializer(Area.objects.filter(parent=None), many=True).data,
            "interests": InterestSerializer(Interest.objects.all(), many=True).data,
            "digital_levels": DigitalLevelSerializer(DigitalLevel.objects.all(), many=True).data,
            "age_groups": AgeGroupSerializer(AgeGroup.objects.all(), many=True).data
        })
