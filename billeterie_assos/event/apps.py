from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EventConfig(AppConfig):
    name = 'event'
    verbose_name = _('event')

    def ready(self):
        import event.signals  # noqa
