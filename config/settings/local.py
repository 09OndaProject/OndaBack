import random

from config.settings.base import ENV

DEBUG = True
ALLOWED_HOSTS = []

# DEBUG = False
# ALLOWED_HOSTS: list[str] = [
#     "127.0.0.1",
#     "localhost",
# ]

# 소셜로그인에 사용할 url (테스트용)
FRONTEND_URL = "http://127.0.0.1:8000/api"


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
