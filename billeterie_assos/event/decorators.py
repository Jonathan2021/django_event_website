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


def can_delete_assos(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = models.Association.objects.get(pk=kwargs['pk'])
        if request.user.has_perm('delete_association', asso):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
