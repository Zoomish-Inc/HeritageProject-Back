from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_files', '0003_mediafile_file_optional'),
        ('heritage', '0007_beforeafterpair_urls'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MediaFile',
        ),
    ]
