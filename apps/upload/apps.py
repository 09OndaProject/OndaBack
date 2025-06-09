from django.apps import AppConfig


class UploadConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.upload"

    def ready(self):
        import apps.upload.signals  # 시그널 연결
