import mimetypes
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image as PilImage

if settings.DJANGO_ENV == "prod":
    from storages.backends.s3boto3 import S3Boto3Storage

    class MediaStorage(S3Boto3Storage):
        location = "media"
        file_overwrite = False  # 파일 덮어쓰기 허용x 랜덤한 문자열 자동 추가

else:
    from django.core.files.storage import FileSystemStorage

    class MediaStorage(FileSystemStorage):
        location = "media"


def upload_to(instance, filename):  # 인스턴스는 file모델. filename은 저장된 파일의 이름
    category = instance.category if instance.category else "other"
    date_path = datetime.now().strftime("%Y/%m/%d")
    return f"{category}/origianl/{date_path}/{filename}"


def thumbnail_upload_to(
    instance, filename
):  # 인스턴스는 file모델. filename은 저장된 파일의 이름
    category = instance.category if instance.category else "other"
    date_path = datetime.now().strftime("%Y/%m/%d")
    return f"{category}/thumbnail/{date_path}/{filename}"


class FileCategory(models.TextChoices):
    POST = "post", "게시글"
    PROFILE = "profile", "프로필"
    MEET = "meet", "모임"
    CERTIFICATE = "certificate", "증명서"
    OTHER = "other", "기타"


FILE_TYPE_CHOICES = [
    ("image", "Image"),
    ("video", "Video"),
    ("file", "File"),
]

THUMBNAIL_SIZE = (500, 500)


class File(models.Model):
    user = models.ForeignKey(
        "user.User", on_delete=models.SET_NULL, null=True, related_name="files"
    )
    category = models.CharField(max_length=20, choices=FileCategory.choices, null=True)
    file = models.FileField(
        storage=MediaStorage, upload_to=upload_to, blank=True, null=True
    )
    file_type = models.CharField(
        max_length=10, choices=FILE_TYPE_CHOICES, blank=True, null=True
    )  # file, video, file
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    thumbnail = models.ImageField(
        storage=MediaStorage, upload_to=thumbnail_upload_to, blank=True, null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.file_name

    class Meta:
        db_table = "file"
        verbose_name = "파일"
        verbose_name_plural = "파일 목록"
        ordering = ["-uploaded_at"]

    # # 이미지 가져오는 메서드
    # def get_image_url(self):
    #     if self.file:
    #         return self.file.url
    #     # 이미지가 없으면 기본이미지 반환
    #     model = self.content_type.model
    #     if model == "user":
    #         return settings.DEFAULT_PROFILE_URL
    #     elif model == "post":
    #         return settings.DEFAULT_POST_URL
    #     return settings.DEFAULT_THUMBNAIL_URL  # 예외 대비 fallback
    #
    # # 썸네일 이미지 가져오는 메서드
    # def get_thumbnail_image_url(self):
    #     if self.thumbnail:
    #         return self.thumbnail.url
    #     elif self.file:
    #         return self.file.url
    #     # 이미지가 없으면 기본이미지 반환
    #     model = self.content_type.model
    #     if model == "user":
    #         return settings.DEFAULT_PROFILE_THUMBNAIL_URL
    #     elif model == "post":
    #         return settings.DEFAULT_POST_THUMBNAIL_URL
    #     return settings.DEFAULT_THUMBNAIL_URL  # 예외 대비 fallback

    def download_from_url(self, url):

        filename = f"profile_{uuid4().hex}.jpeg"

        try:
            response = requests.get(url, stream=True, timeout=5)
            response.raise_for_status()  # 실패 응답을 받을시 예외 발생

            image_file = BytesIO(response.content)
            image_file.seek(0)

            temp_file = ContentFile(image_file.read(), name=filename)
            self.file = temp_file

            return True

        except Exception as e:
            print(f"[File.download_from_url] Failed: {e}")
            return False

    def prepare(self, *, format="WEBP", quality=85, size=None):
        """파일 저장 전에 썸네일 생성, 파일 형식 변환 등 전처리"""

        # self.file_name = os.path.basename(self.file.name)
        self.file_name = self.file.name
        self.file_size = self.file.size
        self.file_type = get_file_type(self.file_name)

        # 이미지라면 변환/썸네일
        if self.file_type == "image":
            image = PilImage.open(self.file)
            # 원본이 RGBA(투명 포함)나 P(팔레트 기반)이면 WebP 저장 시 오류 발생 가능성 있음
            image = image.convert("RGB")

            # 사이즈 옵션이 있으면 리사이징
            if size:
                image.thumbnail((size, size))

            # 메모리 버퍼에 저장 (이미지 임시 저장)
            temp_image = BytesIO()
            converted_format = format.upper()
            image.save(temp_image, format=converted_format, quality=quality)
            temp_image.seek(0)

            # 파일명 변경
            base_name = Path(self.file.name).stem
            new_file_name = f"{base_name}.{format.lower()}"

            # 파일 필드 교체
            self.file.save(new_file_name, ContentFile(temp_image.read()), save=False)
            self.file_name = new_file_name
            self.file_size = self.file.size
            temp_image.close()

            # 썸네일 고정 사이즈 생성
            thumbnail = image.copy()
            thumbnail.thumbnail(THUMBNAIL_SIZE)

            # 변환된 이미지 저장
            temp_thumb = BytesIO()
            thumbnail_filename = f"{base_name}_thumb.{format.lower()}"
            thumbnail.save(temp_thumb, format=converted_format, quality=quality)
            temp_thumb.seek(0)

            self.thumbnail.save(
                thumbnail_filename, ContentFile(temp_thumb.read()), save=False
            )
            temp_thumb.close()

    # 소프트 딜리트 후 주기적으로 한번에 삭제
    # 다른 모델이 소프트 딜리트 시엔 파일 모델 영향없음
    # 하드 딜리트 되면 실제 파일도 필요없음.
    def delete(self, soft=True, using=None, keep_parents=False):
        if soft:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()
        else:
            # 실제 파일이 존재하면 삭제
            if self.file and os.path.isfile(self.file.path):
                self.file.delete(save=False)
            if self.thumbnail and os.path.isfile(self.thumbnail.path):
                self.thumbnail.delete(save=False)
            # DB 레코드 삭제
            super().delete(using=using, keep_parents=keep_parents)


def get_file_type(file_name: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_name)

    if mime_type:
        if mime_type.startswith("image"):
            return "image"
        elif mime_type.startswith("video"):
            return "video"
        else:
            return "file"
    else:
        return "file"  # fallback


# BytesIO()는 Python의 표준 라이브러리 io 모듈에서 제공하는 메모리 기반의 이진 스트림 객체.
# 쉽게 말해, 파일처럼 쓸 수 있는 메모리 상의 버퍼
# 임시로 디스크에 저장하지 않고 이미지 데이터를 처리

# GenericForeignKey는 Django의 ContentTypes 프레임워크에서 제공하는 기능으로,
# **한 모델이 여러 다른 모델(Post, User 등)과 동적으로 관계를 맺을 수 있도록 해주는 "다형적 외래키(polymorphic foreign key)"**입니다.
#
# CREATE TABLE file (
#     id               BIGINT PRIMARY KEY,
#     file            VARCHAR, -- 업로드된 이미지 경로
#     uploaded_at      DATETIME,
#     content_type_id  INTEGER,  -- 연결된 모델의 ID (예: post, user 등)
#     object_id        INTEGER   -- 연결된 모델의 실제 인스턴스 PK
# );
#
# 2024/4/23일
# blog/2024/4/23/이미지파일.jpg
# ImageField, FieldField와 같은데 이미지만 업로드하게 되어있다.
# varchar => 경로만 저장을 함
# 이미지 필드를 사용하기 위해 pillow설  poetry add pillow

# models.CASCATE => 같이 삭제 => 유저 삭제시 같이 블로그도 같이 삭제
# models.PROTECT => 삭제가 불가능함 => 유저를 삭제하려고 할 때 블로그가 있으면 유저 삭제가 불가능 (기본값)
# models.SET_NULL => 널 값을 넣음 => 유저 삭제시 블로그의 author가 Null이 됨.
