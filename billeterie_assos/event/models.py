from django.db import models
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class Email(models.Model):
    email = models.EmailField(_("Email address"))

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")


"""
class Address(models.Model):
    zip_code = models.CharField(max_length=5, validators=[validate_zipcode]
"""


def validate_birth(value):
    if value > datetime.date.today():
        raise ValidationError(_('%(value) is bigger than today'),
                              params={'value': value},)


class User(models.Model):
    email_id = models.ForeignKey(Email, on_delete=models.RESTRICT)
    firstname = models.CharField(_("First name"), max_length=64)
    lastname = models.CharField(_("Last name"), max_length=64)
    gender = models.BooleanField(_("Gender"))
    birth_date = models.DateField(_("Birth Date"), validators=[validate_birth])
    # status = models.IntegerField()
    # adress_id = models.ForeignKey(Address,
    # on_delete = models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class Association(models.Model):
    name = models.CharField(_("Name"), max_length=64)

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
