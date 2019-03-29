from django.db import models
from address.models import AddressField
from compositefk.fields import CompositeOneToOneField
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class Email(models.Model):
    email = models.EmailField(_("Email address"), unique=True)

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")


def validate_birth(value):
    if value > datetime.date.today():
        raise ValidationError(_('%(value) is bigger than today'),
                              params={'value': value},)


class User(models.Model):
    email_id = models.OneToOneField(Email, on_delete=models.PROTECT)
    firstname = models.CharField(_("First name"), max_length=64)
    lastname = models.CharField(_("Last name"), max_length=64)
    gender = models.BooleanField(_("Gender"))
    birth_date = models.DateField(_("Birth Date"), validators=[validate_birth])
    # status = models.IntegerField()
    adress_id = AddressField(null=True, blank='', on_delete=models.SET_NULL)
    # on_delete = models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class Association(models.Model):
    name = models.CharField(_("Name"), max_length=64, unique=True)

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")


class Member(models.Model):
    assos_id = models.ForeignKey(Association, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        unique_together = ('assos_id', 'user_id')


class Manager(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    assos_id = models.ForeignKey(Association, on_delete=models.CASCADE)
    member = CompositeOneToOneField(Member, on_delete=models.CASCADE,
                                    to_fields={"assos_id", "user_id"})

    class Meta:
        verbose_name = _("Member of the Bureau")
        verbose_name_plural = _("Members of the Bureau")


class President(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    assos_id = models.OneToOneField(Association, on_delete=models.CASCADE)
    manager = CompositeOneToOneField(Manager, on_delete=models.CASCADE,
                                     to_fields={"assos_id", "user_id"})

    class Meta:
        verbose_name = _("President")
        verbose_name_plural = _("Presidents")


class Event(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    REFUSED = 'R'
    ONGOING = 'O'
    FINISHED = 'F'
    EVENT_STATE_CHOICES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
        (REFUSED, _("Refused")),
        (ONGOING, _("Ongoing")),
        (FINISHED, _("Finished")),
    )
    event_state = models.CharField(_("State of the event"), max_length=1,
                                   choices=EVENT_STATE_CHOICES,
                                   default=PENDING)
    manager_id = models.ForeignKey(Manager, on_delete=models.SET_NULL,
                                   null=True)
    assos_id = models.ForeignKey(Association,
                                 on_delete=(models.CASCADE
                                            if (event_state == FINISHED or
                                                event_state == REFUSED)
                                            else models.PROTECT))
    address_id = AddressField(on_delete=models.PROTECT)
    # default=epita's address
    premium_flag = models.BooleanField(_("Premium"), default=False)

    class Meta:
        verbose_name = (_("Event"))
        verbose_name_plural = (_("Events"))


INTERN = 'I'
EXTERN = 'E'
STAFF = 'S'
TICKET_TYPE_CHOICES = (
    (INTERN, _("Internal")),
    (EXTERN, _("External")),
    (STAFF, _("Staff")),
)


class Ticket(models.Model):
    ticket_type = models.CharField(_("Type of ticket"), max_length=1,
                                   choices=TICKET_TYPE_CHOICES)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")


class Price(models.Model):
    ticket_type = models.CharField(_("Type of ticket"), max_length=1,
                                   choices=TICKET_TYPE_CHOICES)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_("Price"))

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = ('ticket_type', 'event_id')


class Purchase(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_id = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        unique_together = ('event_id', 'user_id', 'ticket_id')
