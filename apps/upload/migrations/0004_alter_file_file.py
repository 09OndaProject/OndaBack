from django.db import migrations, models

import apps.upload.models


class Migration(migrations.Migration):

    dependencies = [
        ("upload", "0003_file_category_alter_file_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="file",
            field=models.FileField(
                storage=apps.upload.models.MediaStorage,
                upload_to=apps.upload.models.upload_to,
            ),
        ),
    ]
