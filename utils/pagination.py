from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # 개별 뷰에 적용할 페이지 크기
    page_size_query_param = "page_size"  # 클라이언트에서 동적으로 크기 변경 허용
    max_page_size = 50  # 최대 허용 크기


# 클라이언트가 ?page_size=20 식으로 요청 가능
