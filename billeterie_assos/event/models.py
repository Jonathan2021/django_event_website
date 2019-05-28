from django.db import models
# from django.core.validators import validate_email
from django.contrib.auth.models import User
from address.models import AddressField
from compositefk.fields import CompositeOneToOneField
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Create your models here.

User._meta.get_field('email').blank = False


def validate_birth(value):
    if value >= datetime.date.today():
        raise ValidationError(_('%(value) is bigger than today'),
                              params={'value': value},)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    gender = models.BooleanField(_("Gender"), null=True, blank=True)
    birth_date = models.DateField(_("Birth Date"), validators=[validate_birth],
                                  null=True, blank=True)
    address_id = AddressField(null=True, blank=True, related_name="emails",
                              on_delete=models.SET_NULL)

    def __str__(self):
        return '%s (%s)' % (self.user.get_full_name(), self.user.email)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class EmailAddress(models.Model):
    email = models.EmailField(_("Email address"), unique=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % (self.email)

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")


class Association(models.Model):
    name = models.CharField(_("Name"), max_length=64, unique=True)

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")

    def __str__(self):
        return '%s' % (self.name)


class Member(models.Model):
    assos_id = models.ForeignKey(Association, related_name='members',
                                 on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='memberships',
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        unique_together = ('assos_id', 'user')


class Manager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assos_id = models.ForeignKey(Association, on_delete=models.CASCADE,
                                 related_name='managers')
    member = CompositeOneToOneField(Member, on_delete=models.CASCADE,
                                    to_fields={"assos_id", "user"})

    def clean(self):
        super(Manager, self).clean()
        member_id = getattr(self.member, 'id')
        if (member_id is None):
            raise ValidationError(_("Can't create Manager where id of member\
 referenced is None"))
        else:
            try:
                Member.objects.get(pk=member_id)
            except Member.DoesNotExist:
                raise ValidationError({'member': _("Matching member does not \
exist, it was probably deleted")})

    class Meta:
        verbose_name = _("Member of the Bureau")
        verbose_name_plural = _("Members of the Bureau")


class President(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assos_id = models.OneToOneField(Association, on_delete=models.CASCADE,
                                    related_name='president')
    manager = CompositeOneToOneField(Manager, on_delete=models.CASCADE,
                                     to_fields={"assos_id", "user"})

    def clean(self):
        super(President, self).clean()
        manager_id = getattr(self.manager, 'id')
        if (manager_id is None):
            raise ValidationError(_("Can't create President where id of \
manager referenced is None"))
        else:
            try:
                Manager.objects.get(pk=manager_id)
            except Manager.DoesNotExist:
                raise ValidationError({'manager': _("Matching Manager does not \
exist, it was probably deleted")})

    class Meta:
        verbose_name = _("President")
        verbose_name_plural = _("Presidents")


class Event(models.Model):

    PENDING = 'P'
    APPROVED = 'A'
    REFUSED = 'R'
    CANCELED = 'C'
    EVENT_STATE_CHOICES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
        (REFUSED, _("Refused")),
        (CANCELED, _("Canceled")),
    )

    title = models.CharField(_("Title of the event"), max_length=64)
    event_state = models.CharField(_("State of the event"), max_length=1,
                                   choices=EVENT_STATE_CHOICES,
                                   default=PENDING)
    manager_id = models.ForeignKey(Manager, on_delete=models.SET_NULL,
                                   null=True)
    start = models.DateTimeField(_("Start date and time"))
    end = models.DateTimeField(_("End date and time"))
    assos_id = models.ForeignKey(Association, on_delete=models.CASCADE,
                                 related_name='events')
    address_id = AddressField(on_delete=models.PROTECT)
    # default=epita's address
    premium_flag = models.BooleanField(_("Premium"), default=False)

    def clean(self):
        super(Event, self).clean()
        if self.start is not None and self.end is not None and\
                self.start >= self.end:
            raise ValidationError(_('Your event should end after it starts.'))

    class Meta:
        verbose_name = (_("Event"))
        verbose_name_plural = (_("Events"))


class Ticket(models.Model):
    INTERN = 'I'
    EXTERN = 'E'
    STAFF = 'S'
    TICKET_TYPE_CHOICES = (
        (INTERN, _("Internal")),
        (EXTERN, _("External")),
        (STAFF, _("Staff")),
    )

    def get_ticket_name(ticket_type):
        for t_tuple in Ticket.TICKET_TYPE_CHOICES:
            if t_tuple[0] == ticket_type:
                return t_tuple[1]
        return None

    ticket_type = models.CharField(_("Type of ticket"), max_length=1,
                                   choices=TICKET_TYPE_CHOICES)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)

    def has_event(self):
        try:
            getattr(self, 'event_id')
        except Event.DoesNotExist:
            return False
        return True

    def clean(self):
        super(Ticket, self).clean()
        if (self.has_event() and
                self.event_id.event_state != Event.APPROVED):
            raise ValidationError({'event_id': _("This event doesn't have the \
approved state")})

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")


def validate_price_for_sqlite(value):
    if value < 0:
        raise (ValidationError
               (_("Your ticket price should be a positive number: got %s") %
                (value)))


class Price(models.Model):
    ticket_type = models.CharField(_("Type of ticket"), max_length=1,
                                   choices=Ticket.TICKET_TYPE_CHOICES)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_("Price"),
                                        validators=[validate_price_for_sqlite])

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = ('ticket_type', 'event_id')

    def __str__(self):
        return _('%s: %d') % (Ticket.get_ticket_name(self.ticket_type),
                              self.price)


class Purchase(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_id = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def has_ticket(self):
        try:
            self.ticket_id is not None
        except Ticket.DoesNotExist:
            return False
        return True

    def has_event(self):
        try:
            self.event_id is not None
        except Event.DoesNotExist:
            return False
        return True

    def clean(self):
        super(Purchase, self).clean()
        if (self.has_event() and self.has_ticket() and
                self.ticket_id.event_id != self.event_id):
            raise ValidationError(_("event_id should be the same as \
                    ticket_id.event_id"))

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")
        unique_together = ('event_id', 'user', 'ticket_id')
