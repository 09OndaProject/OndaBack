import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.options.models.category import Category


@pytest.mark.django_db
def test_category_list_view():
    Category.objects.create(category_name="정보")
    Category.objects.create(category_name="소통")

    client = APIClient()
    url = reverse("option-categories")
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["category_name"] == "정보"
    assert response.data["results"][1]["category_name"] == "소통"
