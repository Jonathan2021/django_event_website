from django.shortcuts import render, get_object_or_404, redirect
from guardian.shortcuts import assign_perm
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.utils import timezone
# from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Event, Association, Member, President, Manager, Ticket,\
        Purchase, EventCalendar
from .forms import AddMemberForm, AssociationForm, CreateEventForm, UserUpdateForm, ProfileUpdateForm, UpdateEventForm
from django.contrib.auth.models import User
from . import decorators
from django.utils.decorators import method_decorator
import datetime
import calendar
from django.urls import reverse
from calendar import HTMLCalendar
from django.utils.safestring import mark_safe
from shop import models as shop_models

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'index.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(start__gt=timezone.now(), premium_flag=True, event_state=Event.APPROVED).order_by('start')

        d = datetime.date.today()
        previous_month = datetime.date(year=d.year, month=d.month, day=1)  # find first day of current month
        previous_month = previous_month - datetime.timedelta(days=1)  # backs up a single day
        previous_month = datetime.date(year=previous_month.year, month=previous_month.month,
                                       day=1)  # find first day of previous month
 
        last_day = calendar.monthrange(d.year, d.month)
        next_month = datetime.date(year=d.year, month=d.month, day=last_day[1])  # find last day of current month
        next_month = next_month + datetime.timedelta(days=1)  # forward a single day
        next_month = datetime.date(year=next_month.year, month=next_month.month,
                                   day=1)  # find first day of next month

        cal = EventCalendar()
        html_calendar = cal.formatmonth(d.year, d.month, withyear=True)
        html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')
        context['calendar'] = mark_safe(html_calendar)
        return context

#Create your views here.

class EventListView(generic.ListView): 
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(end__gt=timezone.now(), event_state=Event.APPROVED).order_by('start')


class EventDetailView(generic.DetailView, generic.edit.FormMixin):
    model = Event
    form_class = UpdateEventForm
    template_name = 'event_detail.html'

    def get_form_kwargs(self):
        kwargs = super(EventDetailView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user, 'instance' : self.get_object()})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('event:event_detail', kwargs={'pk': self.kwargs.get('pk')})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form): #should maybe save in the forms itself
        form.save()
        return super(EventDetailView, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, anchor='my-form'))
        

    def get_context_data(self, **kwargs): # test it in views
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        staff = event.participants.filter(ticket_id__ticket_type=Ticket.STAFF)
        context['staffs'] = staff
        if event.see_remaining:
            all_tickets = event.tickets.all()
            external_left = 0
            internal_left = 0
            staff_left = 0
            for ticket in all_tickets:
                try:
                    ticket.purchase
                except Purchase.DoesNotExist:
                    if ticket.ticket_type == Ticket.EXTERN:
                        external_left += 1
                    if ticket.ticket_type == Ticket.INTERN:
                        internal_left += 1
                    if ticket.ticket_type == Ticket.STAFF:
                        staff_left += 1
            context['extern_left'] = external_left
            context['intern_left'] = internal_left
            context['staff_left'] = staff_left
        return context



@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_create_event, name='dispatch')
class EventCreateView(generic.CreateView):
    form_class = CreateEventForm
    template_name = 'event_new.html'
    model = Event
    success_url = reverse_lazy('event:assos')

    def get_success_url(self):
        return reverse_lazy('event:event_detail', kwargs={'pk' : self.object.pk})

    def get_form_kwargs(self):
        kwargs = super(EventCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user, 'asso' : self.kwargs.pop('asso', None)})
        return kwargs


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_create_event, name='dispatch') #could return Permission denied in form directly
class EventCreateGeneralView(generic.CreateView):
    form_class = CreateEventForm
    template_name = 'event_new.html'
    model = Event

    def get_success_url(self):
        return reverse_lazy('event:event_detail', kwargs={'pk' : self.object.pk})

    def get_form_kwargs(self):
        kwargs = super(EventCreateGeneralView, self).get_form_kwargs()
        kwargs.update({'user' : self.request.user})
        return kwargs


class AssosDetailView(generic.DetailView, generic.edit.FormMixin):
    model = Association
    template_name = 'assos_detail.html'
    form_class = AddMemberForm

    def get_form_kwargs(self):
        kwargs = super(AssosDetailView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user, 'asso' : self.get_object()})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('event:asso_detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assos = self.get_object()
        try:
            president = assos.president
        except President.DoesNotExist:
            president = None
        context['president'] = president
        president = User.objects.none() if president is None else [president.user]
        managers = assos.managers.all().exclude(user__in=president)
        context['managers'] = managers
        managers = managers.values_list('user', flat=True)
        members = assos.members.all().exclude(user__in=managers).exclude(user__in=president)
        context['members'] = members
        events = assos.events.all()
        now = timezone.now()
        context['future_events'] = events.filter(start__gt=now)
        context['ongoing_events'] = events.filter(start__lte=now, end__gt=now)
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super(AssosDetailView, self).form_valid(form)


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


class ProfileView(generic.ListView): #Shouldnt be a list view
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        u_form = UserUpdateForm();
        p_form = ProfileUpdateForm();
        context = super().get_context_data(**kwargs)
        context = { # should append to already existing context
            'u_form': u_form,
            'p_form': p_form
        }
        return context

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start') # why is it getting Events ? It s a profile view xDDDDDDDDDDDDDDD

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_delete_assos, name='dispatch')
class AssosDelete(generic.DeleteView):
    model = Association

    def get_success_url(self):
        index = reverse('event:index')
        url = self.request.META.get('HTTP_REFERER', index)
        avoid = self.request.build_absolute_uri(reverse('event:asso_detail', kwargs={'pk' : self.kwargs.get('pk')}))
        if (url == avoid):
            return index
        return url
     

    def get(self, request, *args, **kwargs):
        return self.post(request, args, kwargs)

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_manage_member, name='dispatch')
class MemberDelete(generic.DeleteView):
    model = Member

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('event:asso_detail', kwargs={'pk': self.kwargs.pop('asso_pk')})


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_manage_manager, name='dispatch')
class ManagerDelete(generic.DeleteView):
    model = Manager

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('event:asso_detail', kwargs={'pk': self.kwargs.pop('asso_pk')})


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_manage_manager, name='dispatch')
class ManagerCreate(generic.View):
    def get(self, request, *args, **kwargs): 
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        member = get_object_or_404(Member, pk=kwargs.pop('pk'))
        manager = Manager(member=member)
        try:
            manager.full_clean()
            manager.save()
        except:
            pass # should probably do something
        return HttpResponseRedirect(reverse_lazy('event:asso_detail', kwargs={'pk':member.assos_id.pk}))


#Add decorators ?
class PresidentCreate(generic.View):
    def get(self, request, *args, **kwargs): 
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        manager = get_object_or_404(Manager, pk=kwargs.pop('pk'))
        try :
            President.objects.get(assos_id=manager.assos_id).delete()
        except President.DoesNotExist:
            pass
        president = President(manager=manager)
        president.full_clean()
        president.save()
        return HttpResponseRedirect(reverse_lazy('event:asso_detail', kwargs={'pk':manager.assos_id.pk}))



class AssosCreateView(generic.CreateView):
    form_class = AssociationForm
    template_name = 'association_new.html'
    
    def get_success_url(self):
        return reverse_lazy('event:asso_detail', kwargs={'pk': self.object.pk})

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_delete_event, name='dispatch')
class EventDelete(generic.DeleteView): #maybe get calling post is a problem, see csrf token
    model = Event

    def get_success_url(self):
        index = reverse_lazy('event:index')
        url = self.request.META.get('HTTP_REFERER', index)
        avoid = self.request.build_absolute_uri(reverse('event:event_detail', kwargs={'pk' : self.kwargs.get('pk')}))
        if (url == avoid):
            return index
        return url

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_make_cancelable, name='dispatch')
class EventCancelable(generic.View):
    def get(self, request, *args, **kwargs):
        return self.post(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs.get('pk'))
        event.event_state = Event.CANCELABLE
        event.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', reverse('event:index')))


# Should probably fuse into a Change state with new state in url
# Or do I really need a view ? Cant I just create a cancel method in event and do event.cancel from template? -> Not very flexible

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(decorators.can_cancel, name='dispatch')
class EventCancel(generic.View):
    def get(self, request, *args, **kwargs):
        return self.post(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs.get('pk'))
        event.event_state = Event.CANCELED
        event.save()
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', reverse('event:index')))


def search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_bar')
        events = Event.objects.filter(end__gt=timezone.now(), event_state=Event.APPROVED)

        matching_events = []
        for event in events:
            if event.title[:len(search_query)] == search_query:
                matching_events.append(event)

    return render(request, 'search_event.html', { 'events':matching_events})

def Upcomming_Events(request):
    user = User.objects.get(id=request.user.id)
    orders = shop_models.Order.objects.filter(user=user)
    events = []
    for order in orders:
        print(order.ticket_id)
        try:
            event = Ticket.objects.get(id=order.ticket_id).event_id
        except Ticket.DoesNotExist:
            continue
        exist = False
        for e in events:
            if e.title == event.title:
                exist = True
        if not exist:
            events.append(event)

    return render(request, 'my_events.html', { 'events':events})
