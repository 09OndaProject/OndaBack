from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from apps.options.models.category import Category
from apps.options.serializers.category import CategorySerializer


@method_decorator(cache_page(60 * 60 * 24, key_prefix="category_list"), name="dispatch")
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="카테고리 목록 조회",
        operation_description="모든 카테고리 옵션 목록을 조회합니다.",
        responses={200: CategorySerializer(many=True)},
        tags=["옵션 API"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
