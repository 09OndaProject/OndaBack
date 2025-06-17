import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.options.models.age_group import AgeGroup


@pytest.mark.django_db
def test_age_group_list_view():
    AgeGroup.objects.create(group=20)
    AgeGroup.objects.create(group=30)

    client = APIClient()
    url = reverse("option-age-groups")
    response = client.get(url, data={"page": "", "page_size": 1000})

    assert response.status_code == 200
    results = response.data.get("results", [])
    assert len(results) == 2
    assert results[0]["group"] == 20
    assert results[1]["group"] == 30
