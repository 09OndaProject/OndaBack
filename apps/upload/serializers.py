from rest_framework import serializers

from .models import File


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = [
            "id",
            "user",
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
            "user",
            "file_type",
            "file_name",
            "file_size",
            "thumbnail",
            "uploaded_at",
        ]

    def create(self, validated_data):
        files = []

        if request := self.context.get("request", None):
            category = request.data.get("category") or "other"  # None, "", 0, [] 등 Falsy 값이면
            category = category.lower()

            for upload_file in request.FILES.getlist("file"):

                file = File(
                    file=upload_file,
                    user=request.user,
                    category=category,
                )
                file.prepare(
                    format=request.data.get("format", "webp").upper(),
                    quality=int(request.data.get("quality", 85)),
                    size=int(request.data.get("size", 500)) or None,
                )
                files.append(file)

        return File.objects.bulk_create(files)  # 리스트 반환
