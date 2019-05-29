# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
# from django.urls import reverse
from django.views import generic
from django.utils import timezone
# from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Event, Association, Member, President
from django.contrib.auth.models import User

from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'premium_event_list'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start')

#Create your views here.

class EventListView(generic.ListView):
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(end__gt=timezone.now()).order_by('start')


class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'event_detail.html'


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
        events = assos.events.all()
        now = timezone.now()
        context['future_events'] = events.filter(start__gt=now)
        context['ongoing_events'] = events.filter(start__lte=now, end__gt=now)
        return context


class MyAssosView(generic.ListView):
    template_name = 'assos_list.html'
    context_object_name = 'assos'

    def get_queryset(self):
        user = self.request.user
        assos_ids = user.memberships.all().values_list('assos_id', flat=True)
        my_assos = Association.objects.filter(id__in=assos_ids).order_by("name")
        return my_assos


class AssosView(generic.ListView):
    template_name = 'assos_list.html'
    context_object_name = 'assos'

    def get_queryset(self):
        return Association.objects.all().order_by("name")


class ProfileView(generic.ListView):
    template_name = 'profile.html'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start')


def view_that_asks_for_money(request):

    # What you want the button to do.
    paypal_dict = {
        "business": "receiver_email@example.com",
        "amount": "10000000.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('your-return-view')),
        "cancel_return": request.build_absolute_uri(reverse('your-cancel-view')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "payment.html", context)
