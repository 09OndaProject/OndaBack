import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.options.models.digital_level import DigitalLevel


@pytest.mark.django_db
def test_digital_level_list_view():
    DigitalLevel.objects.all().delete()
    DigitalLevel.objects.create(level=1, description="디지털 기기 사용이 익숙함 (상)")
    DigitalLevel.objects.create(
        level=2, description="기본적인 디지털 기기 사용 가능 (중)"
    )

    client = APIClient()
    url = reverse("option-digital-levels")

    response = client.get(url, data={"page": "", "page_size": 1000})

    assert response.status_code == 200
    results = response.data.get("results", [])
    assert len(results) == 2
    assert results[0]["level"] == 1
    assert results[1]["level"] == 2
