from django.test import TestCase
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone
from django.db.utils import IntegrityError
# from django.urls import reverse
from django.contrib.auth.models import User
from event.models import Profile, Association, Member, Manager, President, \
        Event, EmailAddress, Ticket, Price, Purchase
from address.models import Address
from django.db.models.deletion import ProtectedError
from django.utils.translation import ugettext_lazy as _

# Create your tests here.


def clean_and_save(element):
    element.full_clean()
    element.save()


def create_user(name='test', mail='test@test.com', passw='S_8472QLqdqd7+'):
    user = User(username=name, email=mail, password=passw)
    clean_and_save(user)
    return user


def create_address():
    address = Address(raw='11 rue du Vert Buisson')
    clean_and_save(address)
    return address


def create_date_time(days=0, hours=0):
    return timezone.now() + datetime.timedelta(days=days, hours=hours)


class ProfileModelTests(TestCase):

    def setUp(self, gender=True, birthdate=create_date_time(days=-1)):
        self.profile = Profile(user=create_user(), gender=gender,
                               birth_date=birthdate,
                               address_id=create_address())

    def test_null_user(self):
        self.profile.user = None
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_with_correct_input(self):
        self.assertTrue(isinstance(self.profile, Profile))
        clean_and_save(self.profile)
        self.profile.address_id = None
        clean_and_save(self.profile)
        self.profile.address_id = Address.objects.create(raw="")
        clean_and_save(self.profile)

    def test_future_birth_date(self):
        self.profile.birth_date = create_date_time(days=1)
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_null_gender(self):
        self.profile.gender = None
        # with self.assertRaises(ValidationError):
        self.profile.full_clean()

    def test_null_birth_date(self):
        self.profile.birth_date = None
        # with self.assertRaises(ValidationError):
        self.profile.full_clean()

    def test_non_unique_user(self):
        clean_and_save(self.profile)
        with self.assertRaises(ValidationError):
            Profile(user=self.profile.user, gender=True,
                    birth_date=self.profile.birth_date,
                    address_id=self.profile.address_id).full_clean()

    def test_str(self):
        self.assertTrue(self.profile.__str__() == ('%s (%s)' %
                        (self.profile.user.get_full_name(),
                         self.profile.user.email)))

    def test_unexistent_user(self):
        self.profile.user.delete()
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_unexistent_address(self):
        self.profile.address_id.delete()
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_user_on_delete_cascade(self):
        clean_and_save(self.profile)
        self.profile.user.delete()
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(pk=self.profile.id)

    def test_address_on_delete_null(self):
        clean_and_save(self.profile)
        self.profile.address_id.delete()
        self.assertTrue(Profile.objects.get(pk=self.profile.id).address_id
                        is None)


def create_profile(name="default_name"):
    profile = Profile(user=create_user(name), gender=True,
                      birth_date=create_date_time(days=-1),
                      address_id=create_address())
    clean_and_save(profile)
    return profile


class EmailAddressModelTests(TestCase):
    def setUp(self):
        self.emails = EmailAddress(email="default.email@django.relou",
                                   profile=create_profile("emailtest"))

    def test_invalid_email(self):
        self.emails.email = "notanemail"
        with self.assertRaises(ValidationError):
            self.emails.full_clean()

    def test_null_email(self):
        self.emails.email = None
        with self.assertRaises(ValidationError):
            self.emails.full_clean()

    def test_not_unique_email(self):
        clean_and_save(self.emails)
        with self.assertRaises(ValidationError):
            EmailAddress(email=self.emails.email,
                         profile=create_profile("lajoconde")).full_clean()

    def test_null_profile(self):
        self.emails.profile = None
        with self.assertRaises(ValidationError):
            self.emails.full_clean()

    def test_unexistent_profile(self):
        self.emails.profile.delete()
        with self.assertRaises(ValidationError):
            self.emails.full_clean()

    def test_profile_on_delete_cascade(self):
        clean_and_save(self.emails)
        self.emails.profile.delete()
        with self.assertRaises(EmailAddress.DoesNotExist):
            EmailAddress.objects.get(pk=self.emails.id)

    def test_str(self):
        self.assertEqual(self.emails.__str__(), self.emails.email)


"""
test_cascade
"""


class AssociationModelTests(TestCase):
    def test_too_long_name(self):
        assos = Association(name="11111111111111111111111111111111111111111111\
                11111111111111111111111111111111111111111111111111111111111111\
                11111111111111111111111111111111111111111111111111111111111111\
                1111111111111111111111111111111111111111111111111111111111111")
        with self.assertRaises(ValidationError):
            assos.full_clean()

    def test_blank_name(self):
        assos = Association(name="")
        with self.assertRaises(ValidationError):
            assos.full_clean()

    def test_null_name(self):
        assos = Association(name=None)
        with self.assertRaises(ValidationError):
            assos.full_clean()

    def test_str(self):
        assos = Association(name="Epinard")
        self.assertIs(assos.name == assos.__str__(), True)

    def test_valid_input(self):
        Association(name="Epinard").full_clean()


def create_association(name="assos_default"):
    assos = Association(name=name)
    clean_and_save(assos)
    return assos


class MemberModelTests(TestCase):
    def setUp(self):
        self.member = Member(assos_id=create_association(),
                             user=create_user())

    def test_null_profile(self):
        self.member.user = None
        with self.assertRaises(ValidationError):
            self.member.full_clean()

    def test_null_assos(self):
        self.member.assos_id = None
        with self.assertRaises(ValidationError):
            self.member.full_clean()

    def test_valid_input(self):
        self.assertTrue(isinstance(self.member, Member))
        clean_and_save(self.member)

    def test_not_unique_combination_profile_assos(self):
        clean_and_save(self.member)
        with self.assertRaises(ValidationError):
            Member(assos_id=self.member.assos_id,
                   user=self.member.user).full_clean()

    def test_unexistent_assos(self):
        self.member.assos_id.delete()
        with self.assertRaises(ValidationError):
            self.member.full_clean()

    def test_unexistent_profile(self):
        self.member.user.delete()
        with self.assertRaises(ValidationError):
            self.member.full_clean()

    def test_assos_on_delete_cascade(self):
        clean_and_save(self.member)
        self.member.assos_id.delete()
        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(pk=self.member.id)

    def test_profile_on_delete_cascade(self):
        clean_and_save(self.member)
        self.member.user.delete()
        with self.assertRaises(Member.DoesNotExist):
            Member.objects.get(pk=self.member.id)


def create_member(assos=None, profile=None):
    assos = create_association() if assos is None else assos
    profile = create_user() if profile is None else profile
    member = Member(assos_id=assos, user=profile)
    clean_and_save(member)
    return member


class ManagerModelTests(TestCase):
    def setUp(self):
        self.member = create_member(create_association("manager_assos"),
                                    create_user("manager"))

    def test_null_profile(self):
        manager = Manager(assos_id=self.member.assos_id, user=None)
        with self.assertRaises(IntegrityError):  # see comment below
            manager.save()

    def test_null_assos(self):
        manager = Manager(assos_id=None, user=self.member.user)
        # If i full_clean doesnt raise ValidationError but
        # RelatedObjectDoesntExist instead
        with self.assertRaises(IntegrityError):
            manager.save()

    def test_null_member(self):
        manager = Manager(member=None)
        with self.assertRaises(IntegrityError):  # see comment above
            manager.save()

    def test_valid_input(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        self.assertTrue(isinstance(manager, Manager))
        clean_and_save(manager)

    def test_not_unique_compositeonetoonefield(self):
        Manager.objects.create(member=self.member)
        manager = Manager(member=self.member)
        with self.assertRaises(ValidationError):
            manager.full_clean()

    def test_no_ref_member_profile_assos_combination(self):
        manager = Manager(user=self.member.user,
                          assos_id=create_association("dummy"))
        with self.assertRaises(Member.DoesNotExist):
            manager.full_clean()

    def test_deleted_assos(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        self.member.assos_id.delete()
        with self.assertRaises(Member.DoesNotExist):
            manager.full_clean()

    def test_deleted_profile(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        self.member.user.delete()
        with self.assertRaises(Member.DoesNotExist):
            manager.full_clean()

    def test_deleted_member(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        manager.full_clean()
        self.member.delete()
        with self.assertRaises(ValidationError):
            manager.full_clean()

    def test_assos_on_delete_cascade(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        clean_and_save(manager)
        manager.assos_id.delete()
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(pk=manager.id)

    def test_profile_on_delete_cascade(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        clean_and_save(manager)
        manager.user.delete()
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(pk=manager.id)

    def test_member_on_delete_cascade(self):
        manager = Manager(assos_id=self.member.assos_id,
                          user=self.member.user)
        clean_and_save(manager)
        manager.member.delete()
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(pk=manager.id)

    def test_member_id_is_none(self):
        self.member.id = None
        manager = Manager(member=self.member)
        with self.assertRaises(ValidationError):
            manager.full_clean()


def create_manager(member=None):
    member = create_member() if member is None else member
    manager = Manager(member=member)
    clean_and_save(manager)
    return manager


class PresidentModelTests(TestCase):
    def setUp(self):
        self.manager = create_manager()

    def test_null_profile(self):
        president = President(assos_id=self.manager.assos_id, user=None)
        with self.assertRaises(IntegrityError):  # see comment below
            president.save()

    def test_null_assos(self):
        president = President(assos_id=None,
                              user=self.manager.user)
        # If I full_clean doesnt raise ValidationError but
        # RelatedObjectDoesntExist instead
        with self.assertRaises(IntegrityError):
            president.save()

    def test_null_manager(self):
        president = President(manager=None)
        with self.assertRaises(IntegrityError):  # see comment above
            president.save()

    def test_valid_input(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        self.assertTrue(isinstance(president, President))
        clean_and_save(president)

    def test_not_unique_compositeonetoonefield(self):
        President.objects.create(manager=self.manager)
        president = President(manager=self.manager)
        with self.assertRaises(ValidationError):
            president.full_clean()

    def test_no_ref_manager_profile_assos_combination(self):
        president = President(user=create_user("president"),
                              assos_id=create_association("president_assos"))
        with self.assertRaises(Manager.DoesNotExist):
            president.full_clean()

    def test_not_unique_assos(self):
        other_manager = create_manager(create_member(
                                       assos=self.manager.assos_id,
                                       profile=create_user("new_profile")))
        President.objects.create(manager=self.manager)
        president = President(manager=other_manager)
        with self.assertRaises(ValidationError):
            president.full_clean()

    def test_deleted_assos(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        self.manager.assos_id.delete()
        with self.assertRaises(Manager.DoesNotExist):
            president.full_clean()

    def test_deleted_profile(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        self.manager.user.delete()
        with self.assertRaises(Manager.DoesNotExist):
            president.full_clean()

    def test_deleted_manager(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        president.full_clean()
        self.manager.delete()
        with self.assertRaises(ValidationError):
            president.full_clean()

    def test_assos_on_delete_cascade(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        clean_and_save(president)
        president.assos_id.delete()
        with self.assertRaises(President.DoesNotExist):
            President.objects.get(pk=president.id)

    def test_profile_on_delete_cascade(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        clean_and_save(president)
        president.user.delete()
        with self.assertRaises(President.DoesNotExist):
            President.objects.get(pk=president.id)

    def test_manager_on_delete_cascade(self):
        president = President(assos_id=self.manager.assos_id,
                              user=self.manager.user)
        clean_and_save(president)
        president.manager.delete()
        with self.assertRaises(President.DoesNotExist):
            President.objects.get(pk=president.id)

    def test_manager_id_is_none(self):
        self.manager.id = None
        president = President(manager=self.manager)
        with self.assertRaises(ValidationError):
            president.full_clean()

    def test_str(self):
        president = President(manager=self.manager)
        self.assertEqual(president.__str__(), "%s from %s" % (
                         president.user.username, president.assos_id.name))


def make_event(title="event_title", state=Event.APPROVED, manager=None,
               assos=None, address=None, start=None, end=None, premium=False):
    if assos is None:
        assos = manager.assos_id if manager is not None else \
                    create_association()
    address = create_address() if address is None else address
    start = create_date_time(days=1) if start is None else start
    end = start + datetime.timedelta(hours=5) if end is None else end
    return Event(title=title, event_state=state,
                 manager_id=manager, assos_id=assos,
                 address_id=address, start=start, end=end,
                 premium_flag=premium)


def create_event(title="event_title", state=Event.APPROVED, manager=None,
                 assos=None, address=None, start=None, end=None,
                 premium=False):
    event = make_event(title, state, manager, assos, address, start,
                       end, premium)
    clean_and_save(event)
    return event


class EventModelTests(TestCase):
    def test_too_long_title(self):
        with self.assertRaises(ValidationError):
            make_event(title="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").full_clean()

    def test_blank_title(self):
        with self.assertRaises(ValidationError):
            make_event(title="").full_clean()

    def test_invalid_event_state(self):
        with self.assertRaises(ValidationError):
            make_event(state='X').full_clean()

    def test_null_title(self):
        with self.assertRaises(ValidationError):
            make_event(title=None).full_clean()

    def test_null_event_state(self):
        with self.assertRaises(ValidationError):
            make_event(state=None).full_clean()

    def test_null_assos_id(self):
        event = make_event()
        event.assos_id = None
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_start_after_end(self):
        event = make_event()
        event.start = event.end + datetime.timedelta(days=1)
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_null_start(self):
        event = make_event()
        event.start = None
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_null_end(self):
        event = make_event()
        event.end = None
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_null_premium_flag(self):
        with self.assertRaises(ValidationError):
            make_event(premium=None).full_clean()

    def test_start_and_end_at_same_time(self):
        event = make_event()
        event.start = event.end
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_valid_input(self):
        event = make_event()
        clean_and_save(event)

    def test_nonexistent_manager(self):
        event = make_event(manager=create_manager())
        event.manager_id.delete()
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_nonexistent_assos(self):
        event = make_event()
        event.assos_id.delete()
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_nonexistent_address(self):
        event = make_event()
        event.address_id.delete()
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_manager_on_delete_setnull(self):
        event = create_event(manager=create_manager())
        event.manager_id.delete()
        self.assertTrue(Event.objects.get(pk=event.id).manager_id is None)

    def test_assos_on_delete_cascade(self):
        event = create_event()
        event.assos_id.delete()
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=event.id)

    def test_address_on_delete_protect(self):
        event = create_event()
        with self.assertRaises(ProtectedError):
            event.address_id.delete()

    def test_get_ticket_name_invalid(self):
        self.assertIs(Ticket.get_ticket_name('X'), None)


class TicketModelTests(TestCase):
    def setUp(self):
        self.ticket = Ticket(ticket_type='I', event_id=create_event())

    def test_invalid_ticket_type(self):
        self.ticket.ticket_type = 'W'
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_blank_ticket_type(self):
        self.ticket.ticket_type = ''
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_null_ticket_type(self):
        self.ticket.ticket_type = None
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_null_event(self):
        self.ticket.event_id = None
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_refused_event(self):
        self.ticket.event_id.event_state = Event.REFUSED
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_pending_event(self):
        self.ticket.event_id.event_state = Event.PENDING
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_canceled_event(self):
        self.ticket.event_id.event_state = Event.CANCELED
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_nonexistent_event(self):
        self.ticket.event_id.delete()
        with self.assertRaises(ValidationError):
            self.ticket.full_clean()

    def test_event_on_delete_cascade(self):
        clean_and_save(self.ticket)
        self.ticket.event_id.delete()
        with self.assertRaises(Ticket.DoesNotExist):
            Ticket.objects.get(pk=self.ticket.id)


def create_ticket(t_type='I', event_id=None):
    event_id = create_event() if event_id is None else event_id
    ticket = Ticket(ticket_type=t_type, event_id=event_id)
    clean_and_save(ticket)
    return ticket


"""
    def test_past_event(self):
    def test_approved_event(self):
"""


class PriceModelTests(TestCase):
    def setUp(self):
        self.price = Price(ticket_type=Ticket.INTERN,
                           event_id=create_event(), price=3)

    def test_invalid_ticket_type(self):
        self.price.ticket_type = 'W'
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_blank_ticket_type(self):
        self.price.ticket_type = ''
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_null_ticket_type(self):
        self.price.ticket_type = None
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_negative_price(self):
        self.price.price = -42
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_null_price(self):
        self.price.price = None
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_null_event(self):
        self.price.event_id = None
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_str(self):
        self.assertIs(_("%s: %d") %
                      (Ticket.get_ticket_name(self.price.ticket_type),
                       self.price.price)
                      == self.price.__str__(), True)

    def test_not_unique_combination_type_event(self):
        clean_and_save(self.price)
        with self.assertRaises(ValidationError):
            Price(ticket_type=self.price.ticket_type,
                  event_id=self.price.event_id,
                  price=42).full_clean()

    def test_valid_input(self):
        clean_and_save(self.price)

    def test_nonexistent_event(self):
        self.price.event_id.delete()
        with self.assertRaises(ValidationError):
            self.price.full_clean()

    def test_event_on_delete_cascade(self):
        clean_and_save(self.price)
        self.price.event_id.delete()
        with self.assertRaises(Price.DoesNotExist):
            Price.objects.get(pk=self.price.id)


class PurchaseModelTests(TestCase):
    def setUp(self):
        event = create_event()
        self.purchase = Purchase(event_id=event,
                                 user=create_user("ldjqnldhzql"),
                                 ticket_id=create_ticket(event_id=event))

    def test_null_event(self):
        self.purchase.event_id = None
        with self.assertRaises(ValidationError):
            self.purchase.full_clean()

    def test_null_profile(self):
        self.purchase.user = None
        with self.assertRaises(ValidationError):
            self.purchase.full_clean()

    def test_null_ticket(self):
        self.purchase.ticket_id = None
        with self.assertRaises(ValidationError):
            self.purchase.full_clean()

    def test_non_corresponding_ticket_and_event(self):
        clean_and_save(self.purchase)
        with self.assertRaises(ValidationError):
            Purchase(event_id=create_event(title="dummy",
                     manager=self.purchase.event_id.manager_id,
                     assos=create_association("blabla")),
                     user=self.purchase.user,
                     ticket_id=self.purchase.ticket_id).full_clean()

    def test_non_unique_combination_ticket_event_profile(self):
        clean_and_save(self.purchase)
        with self.assertRaises(ValidationError):
            Purchase(event_id=self.purchase.event_id,
                     user=self.purchase.user,
                     ticket_id=self.purchase.ticket_id).full_clean()

    def test_valid_input(self):
        clean_and_save(self.purchase)

    def test_unexistent_event(self):
        self.purchase.event_id.delete()
        with self.assertRaises(ValidationError):
            self.purchase.full_clean()

    def test_unexistent_profile(self):
        self.purchase.user.delete()
        with self.assertRaises(ValidationError):
            self.purchase.full_clean()

    def test_non_existent_ticket(self):
        self.purchase.ticket_id.delete()
        with self.assertRaises(ValidationError):
            self.purchase.full_clean()

    def test_event_on_delete_cascade(self):
        clean_and_save(self.purchase)
        self.purchase.event_id.delete()
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(pk=self.purchase.id)

    def test_profile_on_delete_cascade(self):
        clean_and_save(self.purchase)
        self.purchase.user.delete()
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(pk=self.purchase.id)

    def test_ticket_on_delete_cascade(self):
        clean_and_save(self.purchase)
        self.purchase.ticket_id.delete()
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(pk=self.purchase.id)
