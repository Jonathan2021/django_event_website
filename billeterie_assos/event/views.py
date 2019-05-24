# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
# from django.urls import reverse
from django.views import generic
# from django.utils import timezone

from .models import Event, Association, Member

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'premium_event_list'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start')


class MyAssosView(generic.ListView):
    template_name = 'my_assos_list.html'
    context_object_name = 'my_assos'

    def get_queryset(self):
        user = self.request.user
        assos_ids = Member.objects.filter(profile_id=user).values_list('assos_id', flat=True)
        my_assos = Association.objects.filter(id__in=assos_ids)
        return my_assos
