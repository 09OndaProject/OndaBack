import random

from config.settings.base import ENV

DEBUG = True
# DEBUG = False
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "13.209.4.19",
    "onda.n-e.kr",
    "api.ondamoim.com",
]  # EC2 퍼블릭 IP

# 소셜로그인에 사용할 url
FRONTEND_URL = ENV.get("FRONTEND_URL", "https://www.ondamoim.com")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": ENV.get("POSTGRES_HOST", "db"),
        "USER": ENV.get("POSTGRES_USER", "postgres"),
        "PASSWORD": ENV.get("POSTGRES_PASSWORD", "postgres"),
        "NAME": ENV.get("POSTGRES_DB", "oz_collabo"),
        "PORT": ENV.get("POSTGRES_PORT", 5432),
    }
}

# S3 사용시 설정
# (STORAGES['staticfiles'] 설정이 존재하면,
# Django는 STATIC_ROOT를 무시하고 대신 S3에 업로드.
# default 저장할 때 경로
# staticfiles는 collectstatic할 때 사용하는 경로
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": ENV.get("S3_ACCESS_KEY", ""),
            "secret_key": ENV.get("S3_SECRET_ACCESS_KEY", ""),
            "bucket_name": ENV.get("S3_STORAGE_BUCKET_NAME", ""),
            "region_name": ENV.get("S3_REGION_NAME", ""),
            "custom_domain": f'{ENV.get("S3_STORAGE_BUCKET_NAME", "")}.s3.amazonaws.com',
            "location": "media",
            "default_acl": "public-read",
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": ENV.get("S3_ACCESS_KEY", ""),
            "secret_key": ENV.get("S3_SECRET_ACCESS_KEY", ""),
            "bucket_name": ENV.get("S3_STORAGE_BUCKET_NAME", ""),
            "region_name": ENV.get("S3_REGION_NAME", ""),
            "custom_domain": f'{ENV.get("S3_STORAGE_BUCKET_NAME", "")}.s3.amazonaws.com',
            "location": "static",
            "default_acl": "public-read",
        },
    },
}

# custom_domain이 설정되어 있으면, 이 도메인을 사용해서 URL을 생성
# 그렇지 않으면 기본 Amazon S3 URL (s3.{region}.amazonaws.com/{bucket}/...)을 사용

# Static, Media URL 수정
MEDIA_URL = f"https://{ENV.get('S3_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/media/"
STATIC_URL = f"https://{ENV.get('S3_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/static/"

AWS_ACCESS_KEY_ID = ENV.get("S3_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = ENV.get("S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = ENV.get("S3_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = ENV.get("S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = False


# # 기본 이미지 url 설정
# BASE_STATIC_URL = STATIC_URL + "images/"
# # 기본 프로필 이미지 url 설정
# DEFAULT_PROFILE_URL = BASE_STATIC_URL + "default_profile.webp"
# DEFAULT_PROFILE_THUMBNAIL_URL = BASE_STATIC_URL + "default_profile_thumb.webp"
# # 기본 게시글 이미지 url 설정
# DEFAULT_POST_URL = BASE_STATIC_URL + "default_post.webp"
# DEFAULT_POST_THUMBNAIL_URL = BASE_STATIC_URL + "default_post_thumb.webp"
# # 기본 이미지 url 설정
# DEFAULT_THUMBNAIL_URL = BASE_STATIC_URL + "default_thumb.webp"  # 예외 대비
