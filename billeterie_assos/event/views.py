from django.shortcuts import render, get_object_or_404
from guardian.shortcuts import assign_perm
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.utils import timezone
# from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Event, Association, Member, President, Manager
from .forms import AddMemberForm, AssociationForm, CreateEventForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from . import decorators
from django.utils.decorators import method_decorator

# Create your views here.

# redirect to HTTP_REFERER in some cases https://stackoverflow.com/questions/35796195/how-to-redirect-to-previous-page-in-django-after-post-request/35796559

class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(premium_flag=True).exclude(start__lte=timezone.now()).order_by('start')

#Create your views here.

class EventListView(generic.ListView): 
    template_name = 'event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(end__gt=timezone.now()).order_by('start')


class EventDetailView(generic.DetailView):
    model = Event
    template_name = 'event_detail.html'

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

    def form_valid(self, form): #should maybe save in the forms itself
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


class PresidentCreate(generic.View):
    def get(self, request, *args, **kwargs): #should maybe call post and move everything in post
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
