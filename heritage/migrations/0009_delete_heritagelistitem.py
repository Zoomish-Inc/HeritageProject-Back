from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0008_photoitem_year_nullable'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HeritageListItem',
        ),
    ]
