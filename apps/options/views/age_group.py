from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from apps.options.models.age_group import AgeGroup
from apps.options.serializers.age_group import AgeGroupSerializer


@method_decorator(cache_page(60 * 60, key_prefix="age_group_list"), name="dispatch")
class AgeGroupListView(generics.ListAPIView):
    queryset = AgeGroup.objects.all()
    serializer_class = AgeGroupSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="연령대 목록 조회",
        operation_description="모든 연령대 옵션 목록을 조회합니다.",
        responses={200: AgeGroupSerializer(many=True)},
        tags=["옵션 API"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
