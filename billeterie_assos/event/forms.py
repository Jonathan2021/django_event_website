from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Manager, President
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Profile


from .models import Profile


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
