from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from . import models
from functools import wraps
from guardian.shortcuts import get_objects_for_user


def can_create_event(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        pk = kwargs.get('asso', None)
        if pk is not None:
            asso = get_object_or_404(models.Association, pk=pk)
            if request.user.has_perm('create_event', asso) or \
                    request.user.has_perm('event.create_event'):
                return function(request, *args, **kwargs)
        elif get_objects_for_user(request.user, 'create_event',
                                  models.Association.objects.all()):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def can_delete_assos(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['pk'])
        if request.user.has_perm('delete_association', asso) or \
                request.user.has_perm('event.delete_association'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_delete_event(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        event = get_object_or_404(models.Event, pk=kwargs['pk'])
        if request.user.has_perm('remove_event', event.assos_id) or \
                request.user.has_perm('event.remove_event'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_make_cancelable(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        event = get_object_or_404(models.Event, pk=kwargs['pk'])
        if event.is_ok_cancelable() \
                and request.user.has_perm('make_event_cancelable',
                                          event.assos_id):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def can_cancel(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        event = get_object_or_404(models.Event, pk=kwargs['pk'])
        if event.is_ok_cancel() \
                and request.user.has_perm('event.cancel_event'):
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap


def can_manage_member(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['asso_pk'])
        if request.user.has_perm('manage_member', asso) or \
                request.user.has_perm('event.manage_member'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_manage_manager(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['asso_pk'])
        if request.user.has_perm('manage_manager', asso) or \
                request.user.has_perm('event.manage_manager'):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
