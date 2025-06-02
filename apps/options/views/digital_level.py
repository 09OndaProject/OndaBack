from rest_framework import generics
from apps.options.models.digital_level import DigitalLevel
from apps.options.serializers.digital_level import DigitalLevelSerializer

class DigitalLevelListView(generics.ListAPIView):
    queryset = DigitalLevel.objects.all()
    serializer_class = DigitalLevelSerializer
