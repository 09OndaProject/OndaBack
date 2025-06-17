from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from apps.options.models.digital_level import DigitalLevel
from apps.options.serializers.digital_level import DigitalLevelSerializer


@method_decorator(cache_page(60 * 60, key_prefix="digital_level_list"), name="dispatch")
class DigitalLevelListView(generics.ListAPIView):
    queryset = DigitalLevel.objects.all()
    serializer_class = DigitalLevelSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="디지털 수준 목록 조회",
        operation_description="모든 디지털 역량 수준 옵션을 조회합니다.",
        responses={200: DigitalLevelSerializer(many=True)},
        tags=["옵션 API"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
