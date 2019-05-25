# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
# from django.urls import reverse
from django.views import generic
# from django.utils import timezone

from .models import Event, Association, Member, President, Manager
from django.contrib.auth.models import User

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'premium_event_list'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start')


class AssosDetailView(generic.DetailView):
    model = Association
    template_name = 'assos_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assos = self.get_object()
        try:
            president = assos.president.user
        except President.DoesNotExist:
            president = User.objects.none()
        context['president'] = None if not president else User.objects.get(pk=president[0])
        managers = assos.managers.all().values_list('user', flat=True)
        context['managers'] = User.objects.filter(id__in=managers).exclude(id__in=president)
        members = assos.members.all().values_list('user', flat=True)
        context['members'] = User.objects.filter(id__in=members).exclude(id__in=managers).exclude(id__in=president)
        return context


class MyAssosView(generic.ListView):
    template_name = 'assos_list.html'
    context_object_name = 'assos'

    def get_queryset(self):
        user = self.request.user
        assos_ids = Member.objects.filter(user=user).values_list('assos_id', flat=True)
        my_assos = Association.objects.filter(id__in=assos_ids).order_by("name")
        return my_assos


class AssosView(generic.ListView):
    template_name = 'assos_list.html'
    context_object_name = 'assos'

    def get_queryset(self):
        return Association.objects.all().order_by("name")
