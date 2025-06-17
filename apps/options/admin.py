from django.contrib import admin

from .models import AgeGroup, Area, Category, DigitalLevel, Interest


class ReadOnlyAdmin(admin.ModelAdmin):
    """공통: 추가/삭제 제한"""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AgeGroup)
class AgeGroupAdmin(ReadOnlyAdmin):
    list_display = ("id", "group")


@admin.register(Area)
class AreaAdmin(ReadOnlyAdmin):
    list_display = ("id", "area_name", "depth", "parent")
    list_filter = ("depth",)  # 필터링 가능


@admin.register(Category)
class CategoryAdmin(ReadOnlyAdmin):
    list_display = ("id", "category_name")


@admin.register(DigitalLevel)
class DigitalLevelAdmin(ReadOnlyAdmin):
    list_display = ("id", "level", "description")


@admin.register(Interest)
class InterestAdmin(ReadOnlyAdmin):
    list_display = ("id", "interest_name")
