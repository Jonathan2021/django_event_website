from django import forms
from address.models import Address
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Manager, President, Profile, Association, Event, Ticket, Price, Purchase
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import DateTimeInput, HiddenInput
from guardian.shortcuts import assign_perm, get_objects_for_user
from event.tests.test_models import create_member


class AddMemberForm(forms.Form):
        def __init__(self, *args, **kwargs):
            self.asso = kwargs.pop('asso')
            self.user = kwargs.pop('user')
            super(AddMemberForm,self).__init__(*args,**kwargs)
            unwanted = self.asso.members.all().values_list('user', flat=True)
            self.fields['users'].queryset = User.objects.all().exclude(id__in=unwanted).order_by('username')

        users = forms.ModelMultipleChoiceField(label=_("Members to add"),
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={"class" : "form-control select-multiple"}),
        required=False)

        def save(self, commit=True):
            if not (self.user.has_perm('manager_member', self.asso) or self.user.has_perm('event.manage_member')):
                    raise PermissionDenied
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
        self.fields['address_id'].initial = Address.objects.get_or_create(raw="")[0]
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
    staff_number = forms.IntegerField(label=_("Number of staff"), min_value=0, initial=0)

    class Meta:
        model = Event
        fields = ['title', 'start', 'end', 'assos_id', 'address_id', 'premium_flag', 'image', 'ticket_deadline', 'see_remaining']

    def save(self, commit=True):
        address = self.cleaned_data['address_id']
        self.cleaned_data['address_id'] = None
        obj = Address.objects.get_or_create(raw=address)[0]
        event = super(CreateEventForm, self).save(commit=False)
        event.address_id = obj
        if not (self.user.has_perm('create_event', event.assos_id) or self.user.has_perm('event.create_event')):
            raise PermissionDenied
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


class UpdateEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        """
        self.user = kwargs.pop('user', None) # Should never be None
        if self.user is None:
            raise PermissionDenied # Idk if this is the right error I should raise
        """
        self.event = kwargs.pop('instance')
        super(UpdateEventForm, self).__init__(*args, **kwargs)
        """
        self.fields['title'].widget.attrs.update({"value" : self.event.title})
        self.fields['start'].widget = DateTimeInput(attrs={"value" : self.event.start})
        self.fields['end'].widget = DateTimeInput(attrs={"value" : self.event.end})
        self.fields['address_id'].widget.attrs={"value" : self.event.address_id}
        self.fields['image'].widget.attrs.update({"value" : self.event.image})
        self.fields['ticket_deadline'].widget.attrs.update({"value" : self.event.ticket_deadline})
        self.fields['see_remaining'].widget.attrs.update({"value" : self.event.see_remaining})
        self.fields['premium_flag'].widget.attrs.update({"value" : self.event.premium_flag})
        """
        self.intern = self.event.tickets.filter(ticket_type=Ticket.INTERN)
        self.extern = self.event.tickets.filter(ticket_type=Ticket.EXTERN)
        self.staff = self.event.tickets.filter(ticket_type=Ticket.STAFF)
        self.nb_intern = self.intern.count()
        self.nb_extern = self.extern.count()
        self.nb_staff = self.staff.count()
        self.intern_purchase = self.event.participants.filter(ticket_id__ticket_type=Ticket.INTERN)
        self.intern_purchase_nb = self.intern_purchase.count()
        self.extern_purchase = self.event.participants.filter(ticket_id__ticket_type=Ticket.EXTERN)
        self.extern_purchase_nb = self.extern_purchase.count()
        self.staff_purchase = self.event.participants.filter(ticket_id__ticket_type=Ticket.STAFF)
        self.staff_purchase_nb = self.staff_purchase.count()
        self.fields['title'].required = False
        self.fields['start'].required = False
        self.fields['end'].required = False
        self.fields['image'].required = False
        self.fields['ticket_deadline'].required = False
        self.fields['see_remaining'].required = False
        self.fields['premium_flag'].initial = self.event.premium_flag
        self.fields['start'].widget = DateTimeInput(attrs={"placeholder" : "2017-12-25 14:30:59"})
        self.fields['end'].widget = DateTimeInput(attrs={"placeholder" : "2017-12-25 14:30:59"})
        self.fields['address_id'].label = _("Address")
        self.fields['address_id'].initial = Address.objects.get_or_create(raw="")[0]
        self.fields['address_id'].required = False 
        intern_field = self.fields['intern_number']
        intern_field.widget.attrs['min'] = self.intern_purchase_nb
        intern_field.initial = self.nb_intern
        intern_field.help_text = _('total : %d | bought : %d') % \
                (self.nb_intern, self.intern_purchase_nb)
        extern_field = self.fields['extern_number']
        extern_field.widget.attrs['min'] = self.extern_purchase_nb
        extern_field.initial = self.nb_extern
        extern_field.help_text = _('total : %d | bought : %d') % \
                (self.nb_extern, self.extern_purchase_nb)
        staff_field = self.fields['staff_number']
        staff_field.widget.attrs['min'] = self.staff_purchase_nb
        staff_field.initial = self.nb_staff
        staff_field.help_text = _('total : %d | selected staff: %d') % \
                (self.nb_staff, self.staff_purchase_nb)
        staffs_field = self.fields['staffs']
        # should maybe make a staff model with an event and a member
        # would select members from asso where not already staff
        wanted = self.event.assos_id.members.all().values_list('user', flat=True)
        unwanted = self.event.participants.filter(ticket_id__ticket_type=Ticket.STAFF).values_list('user', flat=True)
        staffs_field.queryset = User.objects.filter(id__in=wanted).exclude(id__in=unwanted)

        try:
            price = self.event.prices.get(ticket_type=Ticket.INTERN).price
            intern_price = self.fields['intern_price']
            intern_price.initial = price
            intern_price.help_text = _('current price in shop is %d') % price
        except Price.DoesNotExist:
            pass
        try:
            price = self.event.prices.get(ticket_type=Ticket.EXTERN).price
            extern_price = self.fields['extern_price']
            extern_price.initial = price
            extern_price.help_text = _('current price in shop is %d') % price
        except Price.DoesNotExist:
            pass

        if not self.user.has_perm('event.choose_premium'):
            self.fields['premium_flag'].widget = HiddenInput()

    intern_number = forms.IntegerField(label=_("Number of tickets for interns"))
    intern_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)
    extern_number = forms.IntegerField(label=_("Number of tickets for externs"))
    extern_price = forms.IntegerField(label=_("Price"), min_value=0, initial=0)
    staff_number = forms.IntegerField(label=_("Total staff number"))
    staffs = forms.ModelMultipleChoiceField(label=_("Staff to add"),
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={"class" : "form-control select-multiple"}),
        required=False)



    class Meta:
        model = Event
        fields = ['title', 'start', 'end', 'address_id', 'premium_flag', 'image', 'ticket_deadline', 'see_remaining']

    def clean_staffs(self):
        value = self.cleaned_data['staffs']
        maximum = self.cleaned_data['staff_number']
        if len(value) + self.staff_purchase_nb > maximum and maximum >= self.nb_staff:
            raise forms.ValidationError(_("You can't have more than %d staffs on this event") %
                                        (maximum))
        return value

    def save(self, commit=True):
        title = self.cleaned_data['title']
        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        premium_flag = self.cleaned_data['premium_flag']
        image = self.cleaned_data['image']
        address = self.cleaned_data['address_id']
        ticket_deadline = self.cleaned_data['ticket_deadline']
        see_remaining = self.cleaned_data['see_remaining']
        intern_number = self.cleaned_data['intern_number']
        extern_number = self.cleaned_data['extern_number']
        staff_number = self.cleaned_data['staff_number']
        intern_price = self.cleaned_data['intern_price']
        extern_price = self.cleaned_data['extern_price']
        staffs = self.cleaned_data['staffs']

        if title:
            self.event.title = title
        if start:
            self.event.start = start
        if end:
            self.event.end = end
        self.event.premium_flag = premium_flag
        if ticket_deadline:
            self.event.ticket_deadline = ticket_deadline
        if see_remaining:
            self.event.see_remaining = see_remaining
        if image:
            self.event.image = image

        if address:
            obj, created = Address.objects.get_or_create(raw=address)
            self.event.address_id = obj

        if (commit):
            if intern_number < self.nb_intern:
                purchase = self.intern_purchase.values_list('ticket_id', flat=True)
                for ticket in self.intern.exclude(id__in=purchase)[:(self.nb_intern - intern_number)]:
                    ticket.delete()

            elif intern_number > self.nb_intern:
                for i in range(intern_number - self.nb_intern):
                    Ticket.objects.create(ticket_type=Ticket.INTERN, event_id=self.event)

            if intern_number:
                obj, created = Price.objects.get_or_create(ticket_type=Ticket.INTERN, event_id=self.event, defaults={'price': intern_price})
                if not created:
                    obj.price = intern_price
                    obj.save()

            if extern_number < self.nb_extern:
                purchase = self.extern_purchase.values_list('ticket_id', flat=True)
                for ticket in self.extern.exclude(id__in=purchase)[:(self.nb_extern - extern_number)]:
                    ticket.delete()

            elif extern_number > self.nb_extern:
                for i in range(extern_number - self.nb_extern):
                    Ticket.objects.create(ticket_type=Ticket.EXTERN, event_id=self.event)

            if extern_number:
                obj, created = Price.objects.get_or_create(ticket_type=Ticket.EXTERN, event_id=self.event, defaults={'price': extern_price})
                if not created:
                    obj.price = extern_price
                    obj.save()

            if staff_number > self.nb_staff:
                for i in range(staff_number - self.nb_staff):
                    Ticket.objects.create(ticket_type=Ticket.STAFF, event_id=self.event)

            if staff_number < self.nb_staff:
                purchase = self.staff_purchase.values_list('ticket_id', flat=True)
                for staff in self.staff.exclude(id__in=purchase)[:(self.nb_staff - staff_number)]:
                    staff.delete()

            if staffs:
                purchase = self.staff_purchase.values_list('ticket_id', flat=True)
                available = self.staff.exclude(id__in=purchase)
                for user in staffs:
                    Purchase.objects.create(event_id=self.event, user=user, ticket_id=available[0])

            if staff_number:
                obj, created = Price.objects.get_or_create(ticket_type=Ticket.STAFF, event_id=self.event, defaults={'price': 0})



            self.event.save()
        return self.event

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
