from django.urls import path

from apps.options.views.age_group import AgeGroupListView
from apps.options.views.area import AreaListView
from apps.options.views.category import CategoryListView
from apps.options.views.digital_level import DigitalLevelListView
from apps.options.views.interest import InterestListView
from apps.options.views.option_all import OptionAllView

urlpatterns = [
    path("options", OptionAllView.as_view(), name="option-all"),
    path("options/areas", AreaListView.as_view(), name="option-areas"),
    path("options/interests", InterestListView.as_view(), name="option-interests"),
    path("options/age-groups", AgeGroupListView.as_view(), name="option-age-groups"),
    path("options/categories", CategoryListView.as_view(), name="option-categories"),
    path(
        "options/digital-levels", DigitalLevelListView.as_view(), name="option-digital-levels"
    ),
]
