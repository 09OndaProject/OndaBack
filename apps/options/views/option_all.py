from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.options.models import AgeGroup, Area, Category, DigitalLevel, Interest
from apps.options.serializers.age_group import AgeGroupSerializer
from apps.options.serializers.area import AreaSerializer
from apps.options.serializers.category import CategorySerializer
from apps.options.serializers.digital_level import DigitalLevelSerializer
from apps.options.serializers.interest import InterestSerializer


class OptionAllView(APIView):
    @swagger_auto_schema(
        operation_summary="전체 옵션 목록 조회",
        operation_description="카테고리, 지역(시), 관심사, 디지털 수준, 연령대 등 모든 옵션 데이터를 한 번에 조회합니다.",
        responses={
            200: openapi.Response(
                description="성공적으로 옵션 데이터를 반환합니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "categories": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT),
                        ),
                        "areas": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT),
                        ),
                        "interests": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT),
                        ),
                        "digital_levels": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT),
                        ),
                        "age_groups": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            )
        },
        tags=["옵션 API"],
    )
    def get(self, request):
        return Response(
            {
                "categories": CategorySerializer(
                    Category.objects.all(), many=True
                ).data,
                "areas": AreaSerializer(
                    Area.objects.filter(parent=None), many=True
                ).data,
                "interests": InterestSerializer(Interest.objects.all(), many=True).data,
                "digital_levels": DigitalLevelSerializer(
                    DigitalLevel.objects.all(), many=True
                ).data,
                "age_groups": AgeGroupSerializer(
                    AgeGroup.objects.all(), many=True
                ).data,
            }
        )
