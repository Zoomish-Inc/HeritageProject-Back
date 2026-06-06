from django.db import migrations, models

import heritage.fields


def copy_media_file_urls(apps, schema_editor):
    BeforeAfterPair = apps.get_model('heritage', 'BeforeAfterPair')
    MediaFile = apps.get_model('media_files', 'MediaFile')

    for pair in BeforeAfterPair.objects.all():
        changed = False
        if pair.before_id:
            media = MediaFile.objects.filter(pk=pair.before_id).first()
            if media and media.source:
                pair.beforeUrl = media.source
                changed = True
        if pair.after_id:
            media = MediaFile.objects.filter(pk=pair.after_id).first()
            if media and media.source:
                pair.afterUrl = media.source
                changed = True
        if changed:
            pair.save(update_fields=['beforeUrl', 'afterUrl'])


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0006_tour_google_drive'),
        ('media_files', '0003_mediafile_file_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='beforeafterpair',
            name='afterUrl',
            field=heritage.fields.FlexibleUrlField(blank=True, verbose_name='Фото «Стало»'),
        ),
        migrations.AddField(
            model_name='beforeafterpair',
            name='beforeUrl',
            field=heritage.fields.FlexibleUrlField(blank=True, verbose_name='Фото «Было»'),
        ),
        migrations.RunPython(copy_media_file_urls, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='beforeafterpair',
            name='after',
        ),
        migrations.RemoveField(
            model_name='beforeafterpair',
            name='before',
        ),
    ]
