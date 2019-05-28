from django import forms
from django.contrib.auth.models import User
from .models import Member, Manager, President
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Profile

class AddMemberForm(forms.Form):
        def __init__(self, *args, **kwargs):
            self.asso = kwargs.pop('asso')
            super(AddMemberForm,self).__init__(*args,**kwargs)
            unwanted = self.asso.members.all().values_list('user', flat=True)
            self.fields['users'].queryset = User.objects.all().exclude(id__in=unwanted)

        users = forms.ModelMultipleChoiceField(label=_("Members to add"),
        queryset=User.objects.none(),
        widget=forms.SelectMultiple(attrs={"class" : "form-control select-multiple"}))

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
