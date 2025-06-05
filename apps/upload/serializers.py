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
            "user",
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

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     print("4444")
    #
    #     request = self.context.get("request", None)
    #     if request:
    #         if request.method == "POST":
    #             data = {
    #                 "id": data.get("id"),
    #                 "message": "업로드 성공",
    #             }
    #         elif request.method == "PATCH":
    #             data = {
    #                 "id": data.get("id"),
    #                 "message": "수정 성공",
    #             }
    #         elif request.method == "PUT":
    #             data = {
    #                 "id": data.get("id"),
    #                 "message": "전체 수정 성공",
    #             }
    #     else:
    #         data["message"] = "요청 없음"
    #
    #     return data

    def create(self, validated_data):
        files = []

        if request := self.context.get("request", None):
            print("request", request)

            for upload_file in request.FILES.getlist("file"):
                print("uploading file", upload_file)
                file = File(file=upload_file, user=request.user)
                file.prepare(
                    format=request.data.get("format", "webp").upper(),
                    quality=int(request.data.get("quality", 85)),
                    size=int(request.data.get("size", 500)) or None,
                )
                print("test1", file)
                files.append(file)
                print("test2", files)

        return File.objects.bulk_create(files)  # 리스트 반환

    def update(self, instance, validated_data):

        request = self.context.get("request", None)
        new_file = validated_data.get("file", None)

        if new_file and instance.file and instance.file != new_file:
            instance.file.delete(save=False)

        raise_errors_on_nested_writes("update", self, validated_data)
        info = model_meta.get_field_info(instance)

        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save(request=request)
        # instance.save()

        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    # def save(self, **kwargs):
    #     print("66")
    #     request = self.context.get("request")
    #     print("77")
    #     return super().save(request=request, **kwargs)


# FileSerializer.save()  ← 당신이 오버라이드함
# └── BaseSerializer.save() ← DRF가 내부에서 정의
#      ├── self.create() → 당신이 오버라이드한 create()
#      │   └── super().create() → DRF의 ModelSerializer default
#      │       └── ModelClass.objects.create(...) → 모델의 save() 호출됨
