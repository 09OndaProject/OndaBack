from rest_framework import generics
from apps.options.models.category import Category
from apps.options.serializers.category import CategorySerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
