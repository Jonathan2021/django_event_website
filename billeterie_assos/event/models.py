from django.db import models
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Create your models here.


def validate_birth(value):
    if value > datetime.date.today():
        raise ValidationError(_('%(value) is bigger than today'),
                              params={'value': value},)


class User(models.Model):
    email_id = models.ForeignKey(Email, on_delete = models.RESTRICT)
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    gender = models.BooleanField()
    birth = models.DateField(validators=[validate_birth])
    status = models.IntegerField()
    adress_id = models.ForeignKey(Address, on_delete = models.SET_NULL, null=True)
