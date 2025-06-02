from rest_framework import generics
from apps.options.models.interest import Interest
from apps.options.serializers.interest import InterestSerializer

class InterestListView(generics.ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
