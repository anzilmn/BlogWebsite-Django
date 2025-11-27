from django.apps import AppConfig

class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        import web.signals  # ✅ This line is important even if Pylance says it's unused
