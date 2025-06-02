from django.urls import path
from apps.options.views.area import AreaListView
from apps.options.views.interest import InterestListView
from apps.options.views.age_group import AgeGroupListView
from apps.options.views.category import CategoryListView
from apps.options.views.digital_level import DigitalLevelListView
from apps.options.views.option_all import OptionAllView

urlpatterns = [
    path('', OptionAllView.as_view(), name='option-all'),
    path('areas', AreaListView.as_view(), name='option-areas'),
    path('interests', InterestListView.as_view(), name='option-interests'),
    path('age-groups', AgeGroupListView.as_view(), name='option-age-groups'),
    path('categories', CategoryListView.as_view(), name='option-categories'),
    path('digital-levels', DigitalLevelListView.as_view(), name='option-digital-levels'),
]
