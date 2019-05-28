# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
# from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from django.utils import timezone

from event.models import Event

class log(generic.ListView):
    def get(self, request):
        return render(request, "log.html");

class logged(generic.ListView):
    def get(self, request):
        return render(request, "logged.html");


# Create your views here.
