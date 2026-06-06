from django.apps import AppConfig


class HeritageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'heritage'

    def ready(self):
        import heritage.signals  # noqa: F401
