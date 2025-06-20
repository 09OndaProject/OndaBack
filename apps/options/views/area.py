from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.options.models.area import Area
from apps.options.serializers.area import AreaSerializer, AreaSimpleSerializer


@method_decorator(cache_page(60 * 60 * 24, key_prefix="area_list"), name="dispatch")
class AreaListView(APIView):

    @swagger_auto_schema(
        operation_summary="지역 목록 조회",
        operation_description="시/구/동 단위로 지역 목록을 조회합니다. 쿼리 파라미터에 따라 부모 지역 또는 depth 기준으로 조회 가능합니다.",
        manual_parameters=[
            openapi.Parameter(
                "depth",
                openapi.IN_QUERY,
                description="지역 구분: 시, 구, 동",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "parent_id",
                openapi.IN_QUERY,
                description="부모 지역 ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        tags=["옵션 API"],
        responses={200: AreaSimpleSerializer(many=True)},
    )
    def get(self, request):
        depth = request.query_params.get("depth")
        parent_id = request.query_params.get("parent_id")

        queryset = (
            Area.objects.all().select_related("parent").prefetch_related("children")
        )

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id).order_by("id")
            serializer = AreaSimpleSerializer(queryset, many=True)

        elif depth:
            queryset = queryset.filter(depth=depth, parent=None).order_by("id")
            serializer = AreaSerializer(queryset, many=True, context={"depth": 1})

        else:
            queryset = queryset.filter(parent=None).order_by("id")
            serializer = AreaSerializer(queryset, many=True, context={"depth": 1})

        return Response(serializer.data)
