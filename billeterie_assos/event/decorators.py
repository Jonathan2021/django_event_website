from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from . import models
from functools import wraps


def can_create_event(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['asso'])
        if request.user.has_perm('create_event', asso):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_delete_assos(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['pk'])
        if request.user.has_perm('delete_association', asso):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_delete_event(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        event = get_object_or_404(models.Event, pk=kwargs['pk'])
        if request.user.has_perm('delete_event', event):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_manage_member(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['asso_pk'])
        if request.user.has_perm('manage_member', asso):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def can_manage_manager(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        asso = get_object_or_404(models.Association, pk=kwargs['asso_pk'])
        if request.user.has_perm('manage_manager', asso):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
