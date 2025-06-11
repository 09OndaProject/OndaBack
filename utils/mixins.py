# 파일도 같이 지워지게 설정
class FileCleanupMixin:
    file_field_name = "file"  # 필요시 override

    def delete(self, *args, **kwargs):
        file_obj = getattr(self, self.file_field_name, None)
        if file_obj:
            if file_obj.file:
                file_obj.file.delete(save=False)
            file_obj.delete()
        super().delete(*args, **kwargs)
