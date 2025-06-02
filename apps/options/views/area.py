from rest_framework.views import APIView
from rest_framework.response import Response
from apps.options.models.area import Area
from apps.options.serializers.area import AreaSerializer

class AreaListView(APIView):
    def get(self, request):
        parent_id = request.query_params.get('parent_id')
        if parent_id:
            areas = Area.objects.filter(parent_id=parent_id)
        else:
            areas = Area.objects.filter(parent=None)
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data)
