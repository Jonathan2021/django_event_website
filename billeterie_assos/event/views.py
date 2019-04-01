# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
# from django.urls import reverse
from django.views import generic
# from django.utils import timezone

from .models import Event


class IndexView(generic.ListView):
    template_name = 'event/index.html'
    context_object_name = 'premium_event_list'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start')


# Create your views here.
