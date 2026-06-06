from django.db import connection, transaction

from heritage.models import DbHeartbeat, HeritageObject


def ping_database():
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')

    with transaction.atomic():
        heartbeat, _ = DbHeartbeat.objects.select_for_update().get_or_create(
            key='render-keepalive',
            defaults={'ping_count': 0},
        )
        heartbeat.ping_count += 1
        heartbeat.save(update_fields=['ping_count', 'updated_at'])

    published_count = HeritageObject.objects.filter(isPublished=True).count()
    total_count = HeritageObject.objects.count()

    return {
        'ping_count': heartbeat.ping_count,
        'heritage_published': published_count,
        'heritage_total': total_count,
    }
