from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Manager, President, Profile, Association, Event, Ticket, Price
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import DateTimeInput
from guardian.shortcuts import assign_perm

class AddMemberForm(forms.Form):
        def __init__(self, *args, **kwargs):
            self.asso = kwargs.pop('asso', None)
            self.user = kwargs.pop('user', None)
            super(AddMemberForm,self).__init__(*args,**kwargs)
            unwanted = self.asso.members.all().values_list('user', flat=True)
            self.fields['users'].queryset = User.objects.all().exclude(id__in=unwanted)

        users = forms.ModelMultipleChoiceField(label=_("Members to add"),
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={"class" : "form-control select-multiple"}),
        required=False)
        #maybe save here instead of in form_valid


class CreateEventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.asso = kwargs.pop('asso', None)
        self.user = kwargs.pop('user')
        super(CreateEventForm, self).__init__(*args, **kwargs)
        self.fields['start'].widget = DateTimeInput(attrs={"placeholder" : "2017-12-25 14:30:59"})
        self.fields['end'].widget = DateTimeInput(attrs={"placeholder" : "2017-12-25 14:30:59"})
        asso_field = self.fields['assos_id']
        self.fields['address_id'].label = _("Address")
        asso_field.label = _("Association")
        if (self.asso is not None):
            asso_field.initial = self.asso
            asso_field.disabled = True
        if (not self.user.has_perm('event.change_state')):
            state_field = self.fields['event_state']
            state_field.initial = Event.PENDING
            state_field.disabled = True

    intern_number = forms.IntegerField(label=_("Number of tickets for interns"), min_value=0, initial=0)
    intern_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)
    extern_number = forms.IntegerField(label=_("Number of tickets for externs"), min_value=0, initial=0)
    extern_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)
    staff_number = forms.IntegerField(label=_("Number of tickets for staff"), min_value=0, initial=0)
    staff_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)

    class Meta:
        model = Event
        fields = ['title', 'event_state', 'manager_id', 'start', 'end', 'assos_id', 'address_id', 'premium_flag']

    def save(self, commit=True):
        event = super(CreateEventForm, self).save(commit=commit)
        if (commit):
            intern_number = self.cleaned_data['intern_number']
            extern_number = self.cleaned_data['extern_number']
            staff_number = self.cleaned_data['staff_number']
            intern_price = self.cleaned_data['intern_price']
            extern_price = self.cleaned_data['extern_price']
            staff_price = self.cleaned_data['staff_price']
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
            Price.objects.create(ticket_type=Ticket.STAFF, event_id=event, price=staff_price)
        return event


class AssociationForm(forms.ModelForm):
    president = forms.ModelChoiceField(label=_("President"),
            queryset=User.objects.all()) #should make them only from epita        

    class Meta:
        model = Association
        fields = ['name']

    def save(self, commit=True):
        asso = super(AssociationForm, self).save(commit=commit)
        print(asso)
        if (commit):
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
