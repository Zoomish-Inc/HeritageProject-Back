from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0007_beforeafterpair_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photoitem',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
