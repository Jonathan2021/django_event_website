from django.db import models
# from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.core import validators
from address.models import AddressField
from compositefk.fields import CompositeOneToOneField
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import assign_perm, remove_perm
from solo.models import SingletonModel

# Create your models here.

User._meta.get_field('email').blank = False


def validate_birth(value):
    if value >= datetime.date.today():
        raise ValidationError(_('%(value) is bigger than today'),
                              params={'value': value},)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg',
                              upload_to='profile_pics/uploads/')
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

class UnicodeValidator(validators.RegexValidator):
    regex = r'^[\s\w.@+-]+\Z'
    message = _(
        'Enter a valid name for your association. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = 0

class Association(models.Model):
    name = models.CharField(_("Name"), max_length=64, unique=True,
                            validators=[UnicodeValidator()])
    url = models.URLField(_("Association's website"), null=True, blank=True)

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")

        permissions = (
            ('create_event', 'User can create an event'),
            ('manage_member', 'User can add and remove a member'),
            ('choose_staff', 'User can choose staff'),
            ('manage_manager', 'User can add and remove managers'),
            ('modify_event', 'User can modify an event'),
            ('cancel_event', 'User can cancel an event'),
            ('validate_event',
             'User can validate event and make it available for approval')
            # ('manage_president', 'User can modify the president'),
        )

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

    def __str__(self):
        return '%s from %s' % (self.user.username, self.assos_id.name)

    def save(self, *args, **kwargs):
        super(Member, self).save(*args, **kwargs)
        assign_perm('create_event', self.user, self.assos_id)

    def delete(self):
        remove_perm('create_event', self.user, self.assos_id)
        super(Member, self).delete()


class Manager(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="managerships")
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

    def __str__(self):
        return '%s from %s' % (self.user.username, self.assos_id.name)

    def save(self, *args, **kwargs):
        super(Manager, self).save(*args, **kwargs)
        assign_perm('manage_member', self.user, self.assos_id)
        assign_perm('choose_staff', self.user, self.assos_id)

    def delete(self):
        remove_perm('choose_staff', self.user, self.assos_id)
        remove_perm('manage_member', self.user, self.assos_id)
        super(Manager, self).delete()


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

    def __str__(self):
        return '%s from %s' % (self.user.username, self.assos_id.name)

    def save(self, *args, **kwargs):
        super(President, self).save(*args, **kwargs)
        assign_perm('manage_manager', self.user, self.assos_id)
        assign_perm('delete_association', self.user, self.assos_id)
        assign_perm('change_association', self.user, self.assos_id)
        assign_perm('modify_event', self.user, self.assos_id)
        assign_perm('cancel_event', self.user, self.assos_id)
        assign_perm('validate_event', self.user, self.assos_id)

    def delete(self):
        remove_perm('manage_manager', self.user, self.assos_id)
        remove_perm('delete_association', self.user, self.assos_id)
        remove_perm('change_association', self.user, self.assos_id)
        remove_perm('modify_event', self.user, self.assos_id)
        remove_perm('cancel_event', self.user, self.assos_id)
        remove_perm('validate_event', self.user, self.assos_id)
        super(President, self).delete()


class Boss(SingletonModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return u"Boss: %s" % (self.user.username)

    class Meta:
        verbose_name = _("Boss")


class Event(models.Model):

    PENDING = 'P'
    APPROVED = 'A'
    VALIDATED = 'V'
    REFUSED = 'R'
    CANCELED = 'C'
    EVENT_STATE_CHOICES = (
        (PENDING, _("Pending")),
        (APPROVED, _("Approved")),
        (REFUSED, _("Refused")),
        (CANCELED, _("Canceled")),
        (VALIDATED, _("Validated by the president")),
    )

    title = models.CharField(_("Title of the event"), max_length=64)
    event_state = models.CharField(_("State of the event"), max_length=1,
                                   choices=EVENT_STATE_CHOICES,
                                   default=PENDING)
    manager_id = models.ForeignKey(Manager, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    start = models.DateTimeField(_("Start date and time"))
    end = models.DateTimeField(_("End date and time"))
    ticket_deadline = models.DateTimeField(_("Deadline to buy tickets"),
                                           null=True, blank=True)
    # tests for this field
    assos_id = models.ForeignKey(Association, on_delete=models.CASCADE,
                                 related_name='events')
    address_id = AddressField(on_delete=models.PROTECT)
    # default=epita's address
    premium_flag = models.BooleanField(_("Premium"), default=False)
    image = models.ImageField(_("Event's cover image"),
                              default='event_pics/default.jpg',
                              upload_to='event_pics/uploads/')
    see_remaining = models.BooleanField(_("See remaining tickets"),
                                        default=False)

    def clean(self):
        super(Event, self).clean()
        if self.start is not None:
            if self.ticket_deadline is not None and \
                    self.ticket_deadline > self.start:
                raise ValidationError({'ticket_deadline': _(
                    'Ticket deadline should be before the start.')})
            if self.end is not None and\
                    self.start >= self.end:
                raise ValidationError(_(
                    'Your event should end after it starts.'))

    class Meta:
        verbose_name = (_("Event"))
        verbose_name_plural = (_("Events"))

        permissions = (
            ('access_dashboard', 'User can access this event\'s dashboard'),
            ('change_state', 'User can the event\'s state'),
            ('choose_premium', 'User can make an event premium or not'),
        )

    def save(self, *args, **kwargs):
        if self.ticket_deadline is None:
            self.ticket_deadline = self.start # should maybe use signals
        super(Event, self).save(*args, **kwargs)


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
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE,
                                 related_name='tickets')

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
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE,
                                 related_name="Prices")
    price = models.PositiveIntegerField(_("Price"),
                                        validators=[validate_price_for_sqlite])

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = ('ticket_type', 'event_id')

    def __str__(self):
        return _('%s: %d') % (Ticket.get_ticket_name(self.ticket_type),
                              self.price)

    def clean(self):
        super(Price, self).clean()
        if self.ticket_type == Ticket.STAFF and self.price != 0:
            raise ValidationError({'price': _("Staff tickets should be free")})


class Purchase(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE,
                                 related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket_id = models.OneToOneField(Ticket, on_delete=models.CASCADE,
                                     related_name='purchase')

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


"""
class RightsSupport(models.Model):

    class Meta:

        managed = False

        permissions = (
            ('customer_rights', 'Global customer rights'),
            ('vendor_rights', 'Global vendor rights'),
            ('any_rights', 'Global any rights'),
        )
"""
