from django.core.exceptions import PermissionDenied
from . import models
from functools import wraps

def can_create_event(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = models.Association.objects.get(pk=kwargs['asso'])
        if request.user.has_perm('create_event', asso):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
