import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.options.models.interest import Interest


@pytest.mark.django_db
def test_interest_list_view():
    Interest.objects.create(interest_name="건강")
    Interest.objects.create(interest_name="여행")

    client = APIClient()
    url = reverse("option-interests")
    response = client.get(url, data={"page": "", "page_size": 1000})

    assert response.status_code == 200
    results = response.data.get("results", [])
    assert len(results) == 2
    assert results[0]["interest_name"] == "건강"
    assert results[1]["interest_name"] == "여행"
