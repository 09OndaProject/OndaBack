from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from .models import File


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = [
            "id",
            "user_id",
            "category",
            "file",
            "file_type",
            "file_name",
            "file_size",
            "thumbnail",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "user_id",
            "file_type",
            "file_name",
            "file_size",
            "thumbnail",
            "uploaded_at",
        ]

    def create(self, validated_data):
        files = []

        if request := self.context.get("request", None):
            print("request", request)

            for upload_file in request.FILES.getlist("file"):
                print("uploading file", upload_file)
                file = File(
                    file=upload_file,
                    user=request.user,
                    category=validated_data.get("category"),
                )
                file.prepare(
                    format=request.data.get("format", "webp").upper(),
                    quality=int(request.data.get("quality", 85)),
                    size=int(request.data.get("size", 500)) or None,
                )
                print("test1", file)
                files.append(file)
                print("test2", files)

        return File.objects.bulk_create(files)  # 리스트 반환
