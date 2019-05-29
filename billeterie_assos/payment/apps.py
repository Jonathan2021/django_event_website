from django.apps import AppConfig


class EventConfig(AppConfig):
    name = 'payment'

    def ready(self):
        import users.signals
