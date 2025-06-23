from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from apps.options.models.interest import Interest
from apps.options.serializers.interest import InterestSerializer


@method_decorator(cache_page(60 * 60 * 24, key_prefix="interest_list"), name="dispatch")
class InterestListView(generics.ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="관심사 목록 조회",
        operation_description="사용 가능한 관심사 목록을 조회합니다.",
        responses={200: InterestSerializer(many=True)},
        tags=["옵션 API"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
