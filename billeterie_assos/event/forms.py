from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Manager, President, Profile, Association, Event, Ticket, Price
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import DateTimeInput, HiddenInput
from guardian.shortcuts import assign_perm, get_objects_for_user
from event.tests.test_models import create_member


class AddMemberForm(forms.Form):
        def __init__(self, *args, **kwargs):
            self.asso = kwargs.pop('asso', None)
            self.user = kwargs.pop('user', None)
            super(AddMemberForm,self).__init__(*args,**kwargs)
            unwanted = self.asso.members.all().values_list('user', flat=True)
            self.fields['users'].queryset = User.objects.all().exclude(id__in=unwanted).order_by('username')

        users = forms.ModelMultipleChoiceField(label=_("Members to add"),
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={"class" : "form-control select-multiple"}),
        required=False)

        def save(self, commit=True):
            if self.asso is not None:
                for user in self.cleaned_data['users']:
                    create_member(profile=user, assos=self.asso)


class CreateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        """
        self.user = kwargs.pop('user', None) # Should never be None
        if self.user is None:
            raise PermissionDenied # Idk if this is the right error I should raise
        """
        self.asso = kwargs.pop('asso', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['start'].widget = DateTimeInput(attrs={"placeholder" : "2017-12-25 14:30:59"})
        self.fields['end'].widget = DateTimeInput(attrs={"placeholder" : "2017-12-25 14:30:59"})
        asso_field = self.fields['assos_id']
        self.fields['address_id'].label = _("Address")
        asso_field.label = _("Association")
        if (self.asso is not None):
            """
            if not self.user.has_perm('create_event', self.asso):
                raise PermissionDenied # Or maybe all this should be tested in the views
            """
            asso_field.initial = self.asso
            asso_field.disabled = True
        else:
            asso_field.queryset = get_objects_for_user(self.user,
                    'create_event', Association.objects.all())
        if not self.user.has_perm('event.choose_premium'):
            self.fields['premium_flag'].widget = HiddenInput()


    intern_number = forms.IntegerField(label=_("Number of tickets for interns"), min_value=0, initial=0)
    intern_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)
    extern_number = forms.IntegerField(label=_("Number of tickets for externs"), min_value=0, initial=0)
    extern_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)
    staff_number = forms.IntegerField(label=_("Number of tickets for staff"), min_value=0, initial=0)

    class Meta:
        model = Event
        fields = ['title', 'start', 'end', 'assos_id', 'address_id', 'premium_flag', 'image', 'ticket_deadline', 'see_remaining']

    def save(self, commit=True):
        event = super(CreateEventForm, self).save(commit=False)
        if self.user.has_perm('event.approve_event'):
            event.event_state = Event.APPROVED
        elif self.user.has_perm('validate_event', event.assos_id):
            event.event_state = Event.VALIDATED
        if (commit):
            event.save()
            intern_number = self.cleaned_data['intern_number']
            extern_number = self.cleaned_data['extern_number']
            staff_number = self.cleaned_data['staff_number']
            intern_price = self.cleaned_data['intern_price']
            extern_price = self.cleaned_data['extern_price']
            for i in range(intern_number):
                Ticket.objects.create(ticket_type=Ticket.INTERN, event_id=event)
            for i in range(extern_number):
                Ticket.objects.create(ticket_type=Ticket.EXTERN, event_id=event)
            for i in range(staff_number):
                Ticket.objects.create(ticket_type=Ticket.STAFF, event_id=event)
        if (intern_number):
            Price.objects.create(ticket_type=Ticket.INTERN, event_id=event, price=intern_price)
        if (extern_number):
            Price.objects.create(ticket_type=Ticket.EXTERN, event_id=event, price=extern_price)
        if (staff_number):
            Price.objects.create(ticket_type=Ticket.STAFF, event_id=event, price=0)
        return event


class AssociationForm(forms.ModelForm):
    president = forms.ModelChoiceField(label=_("President"),
            queryset=User.objects.all()) #should make them only from epita        

    class Meta:
        model = Association
        fields = ['name', 'url']

    def save(self, commit=True):
        asso = super(AssociationForm, self).save(commit=False)
        asso.full_clean()
        if (commit):
            asso.save()
            president = self.cleaned_data['president'] #should add perms here maybe
            member = Member(user=president, assos_id=asso)
            manager = Manager(member=member)
            pres = President(manager=manager)
            member.full_clean()
            member.save()
            manager.full_clean()
            manager.save()
            pres.full_clean()
            pres.save()
        return asso
    

"""
def add_personnels_to_group(request): # pk is group's pk
    # Recursively add personnels to a group
    template = "personnel/add_personnels_to_group.html"
    # group = Group.objects.get(pk=pk) # replace this

    if request.method == "POST":
        form = AddPersonnelToGroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group'] # replacement
            personnels = [Personnel.objects.get(pk=pk) for pk in request.POST.getlist("personnels", "")]

            for personnel in personnels:
                user = personnel.user
                if user.groups.filter(id=group.id).count():
                    user.groups.remove(group)
                else:
                    user.groups.add(group)
                    msg.append("{} added".format(personnel.display_name))

            return redirect(wherever)
    else:
        form = AddPersonnelToGroupForm()
        return render(request, template, {"form" : form, "group" : group})
"""


class CustomUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class ProfileModelChoiceField(forms.ChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" % (obj.user.get_full_name(), obj.user.username)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class MemberAdminForm(forms.BaseInlineFormSet):
    manager = forms.BooleanField()
    president = forms.BooleanField()
    profile_id = ProfileModelChoiceField

    def clean(self):
        if self.president and not self.manager:
            raise ValidationError(_('A president is necessarily a Member \
                of the Bureau'))
        else:
            super(MemberAdminForm, self).clean()

    def save(self, commit=True):
        member = super(MemberAdminForm, self).save(commit=commit)
        if member.assos_id and member.profile_id:
            if self.manager:
                new_manager = Manager.objects.create(
                        profile_id=member.profile_id,
                        assos_id=member.assos_id
                                                    )
                if self.president:
                    President.object.create(
                            profile_id=new_manager.profile_id,
                            assos_id=new_manager.assos_id
                                           )
            elif self.president:
                raise ValidationError(_('A president is necessarily a Member \
                        of the Bureau (how did it pass first test?)'))
        return member

    class Meta:
        model = Member
        fields = ['assos_id', 'profile_id', 'manager', 'president']


MemberAdminFormset = forms.formset_factory(Member, MemberAdminForm)
