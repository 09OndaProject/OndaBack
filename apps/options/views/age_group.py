from rest_framework import generics

from apps.options.models.age_group import AgeGroup
from apps.options.serializers.age_group import AgeGroupSerializer


class AgeGroupListView(generics.ListAPIView):
    queryset = AgeGroup.objects.all()
    serializer_class = AgeGroupSerializer
