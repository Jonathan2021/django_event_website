# from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy
from django.views import generic
from django.utils import timezone
# from django.utils import timezone

from .models import Event, Association, Member, President
from .forms import AddMemberForm
from django.contrib.auth.models import User

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'premium_event_list'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).order_by('start')


class EventListView(generic.ListView):
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(end__gt=timezone.now()).order_by('start')


class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'event_detail.html'


class AssosDetailView(generic.DetailView, generic.edit.FormMixin):
    model = Association
    template_name = 'assos_detail.html'
    form_class = AddMemberForm

    def get_form(self):
        if self.request.method == 'POST':
            return AddMemberForm(asso=self.get_object(), data=self.request.POST)
        return AddMemberForm(asso=self.get_object())

    def get_success_url(self):
        return reverse_lazy('event:asso_detail', kwargs={'pk': self.object.pk})

    def get_object(self):
        try:
            my_assos = Association.objects.get(pk=self.kwargs.get('pk'))
            return my_assos
        except self.model.DoesNotExist:
            raise Http404("No Association matches the given query.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assos = self.get_object()
        no_pres = False
        try:
            president = assos.president
        except President.DoesNotExist:
            no_pres = True
            president = President.objects.none()
        context['president'] = president
        president = User.objects.none() if no_pres else president.user
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
        print('I POSTED')
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print('FORM INVALID WHAAAT')
            return self.form_invalid(form)

    def form_valid(self, form):
        asso = self.get_object()
        print("I'm HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        users = [User.objects.get(pk=pk) for pk in self.request.POST.getlist("users", "")]
        for user in users:
            Member.objects.create(user=user, assos_id=asso)
        return super(AssosDetailView, self).form_valid(form)

    def form_invalid(self, form):
    #put logic here
        print(form.errors)
        return super(AssosDetailView, self).form_invalid(form)


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

class AssosDelete(generic.DeleteView):
    model = Association
    success_url = reverse_lazy('my_assos')
