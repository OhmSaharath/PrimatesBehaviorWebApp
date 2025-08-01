from django.apps import AppConfig


class PrimatesgameapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PrimatesGameAPI'

    def ready(self):
        import PrimatesGameAPI.signals  # if defined separately