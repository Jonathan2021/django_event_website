from django.contrib.auth.forms import UserCreationForm
from event.models import Profile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError(_("Can't create User and Profile \
without database save"))
        user = super(CustomUserCreationForm, self).save(commit=True)
        profile = Profile(user=user, gender=None,
                          birth_date=None)
        profile.full_clean()
        profile.save()
        return user
