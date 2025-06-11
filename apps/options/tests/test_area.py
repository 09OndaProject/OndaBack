import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.options.models.area import Area


@pytest.mark.django_db
def test_area_list_by_depth():
    # 시 생성
    seoul = Area.objects.create(area_name="서울", depth="시")
    # 구 생성
    gangnam = Area.objects.create(area_name="강남구", depth="구", parent=seoul)
    # 동 생성
    yeoksam = Area.objects.create(area_name="역삼동", depth="동", parent=gangnam)

    client = APIClient()

    # depth=시 요청
    response = client.get(reverse("option-areas"), {"depth": "시"})
    assert response.status_code == 200
    assert response.data[0]["area_name"] == "서울"

    # parent_id=서울.id 요청 → 강남구
    response = client.get(reverse("option-areas"), {"parent_id": seoul.id})
    assert response.status_code == 200
    assert response.data[0]["area_name"] == "강남구"

    # parent_id=강남구.id 요청 → 역삼동
    response = client.get(reverse("option-areas"), {"parent_id": gangnam.id})
    assert response.status_code == 200
    assert response.data[0]["area_name"] == "역삼동"
