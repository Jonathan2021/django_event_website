from django.test import TestCase
from pprint import pprint
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone
from django.db.utils import IntegrityError
# from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile, Association, Member, Manager, President, Event
from address.models import Address

# Create your tests here.
def create_user(name='test', mail='test@test.com',\
        passw='S_8472QLqdqd7+'):
    return User.objects.create(username=name, email=mail, password=passw)


def create_address():
    return Address.objects.create(raw='11 rue du Vert Buisson')


def create_date(days):
    return timezone.now() + datetime.timedelta(days=days)


class ProfileModelTests(TestCase):

    def create_profile(self, gender=True, birthdate=create_date(-1)):
        self.profile = Profile(user=self.user, gender=gender,  birth_date=birthdate,
                address_id=self.address)
  
    def create_all(self):
        self.user = create_user()
        self.address = create_address()

    def test_null_user(self):
        self.address = create_address()
        self.user = None
        self.create_profile()
        with self.assertRaises(ValidationError):
            self.profile.full_clean()
    
    def test_with_correct_input(self):
        self.create_all()
        self.create_profile()
        self.assertTrue(isinstance(self.profile, Profile))
        self.profile.full_clean()
        self.profile.save()

    def test_future_birth_date(self):
        self.create_all()
        self.create_profile(birthdate=create_date(1))
        with self.assertRaises(ValidationError):
            self.profile.full_clean()
 
    def test_null_gender(self):
        self.create_all()
        self.create_profile(gender=None)
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_null_birth_date(self):
        self.create_all()
        self.create_profile(birthdate=None)
        with self.assertRaises(ValidationError):
            self.profile.full_clean()
    
    def test_non__unique_user(self):
        self.create_all()
        self.create_profile()
        self.profile.save()
        self.create_profile()
        with self.assertRaises(IntegrityError):
            self.profile.save()

    def test_profile_str(self):
        self.create_all()
        self.create_profile()
        self.assertTrue(self.profile.__str__() == ('%s (%s)' %\
                (self.user.get_full_name(), self.user.email)))


def create_profile(name="default_name"):
    return Profile.objects.create(user=create_user(name), gender=True,
            birth_date=create_date(-1), address_id=create_address())


# class EmailAddressModelTests(TestCase):


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
    return Association.objects.create(name=name)


class MemberModelTests(TestCase):
    def create_all(self):
        self.assos = create_association()
        self.profile = create_profile()

    def test_null_profile(self):
        self.assos = create_association()
        member = Member(assos_id=self.assos, profile_id=None)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_null_assos(self):
        self.profile = create_profile()
        member = Member(assos_id=None, profile_id=self.profile)
        with self.assertRaises(ValidationError):
            member.full_clean()

    def test_valid_input(self):
        self.create_all()
        member = Member(assos_id=self.assos, profile_id=self.profile)
        self.assertTrue(isinstance(member, Member))
        member.full_clean()

    def test_not_unique_combination_profile_assos(self):
        self.create_all()
        Member.objects.create(assos_id=self.assos, profile_id=self.profile)
        with self.assertRaises(IntegrityError):
            Member.objects.create(assos_id=self.assos, profile_id=self.profile)

def create_member(assos=None, profile=None):
    assos = create_association() if assos is None else assos
    profile = create_profile() if profile is None else profile
    return Member.objects.create(assos_id=assos, profile_id=profile)


class ManagerModelTests(TestCase):
    def create_all(self):
        self.member = create_member(create_association("manager_assos"),
                                    create_profile("manager"))

    def test_null_profile(self):
        self.create_all()
        manager = Manager(assos_id=self.member.assos_id, profile_id=None)
        with self.assertRaises(IntegrityError): #see comment below
            manager.save()

    def test_null_assos(self):
        self.create_all()
        manager = Manager(assos_id=None, profile_id=self.member.profile_id)
        with self.assertRaises(IntegrityError): #If i full_clean doesnt raise ValationError but RelatedObjectDoesntExist instead
            manager.save()

    def test_null_member(self):
        manager = Manager(member=None)
        with self.assertRaises(IntegrityError): #see comment above
            manager.save()

    def test_valid_input(self):
        self.create_all()
        manager = Manager(assos_id=self.member.assos_id,
                          profile_id=self.member.profile_id)
        self.assertTrue(isinstance(manager, Manager))
        manager.full_clean()
        manager.save()

    def test_not_unique_compositeonetoonefield(self):
        self.create_all()
        Manager.objects.create(member=self.member)
        manager = Manager(member=self.member)
        with self.assertRaises(ValidationError):
            manager.full_clean()

    def test_no_ref_member_profile_assos_combination(self):
        manager = Manager(profile_id=create_profile("manager"),
                          assos_id=create_association("manager_assos"))
        with self.assertRaises(Member.DoesNotExist):
            manager.full_clean()
"""
    def test_unknown_profile(self):
    def test_unknow_assos(self):
"""

def create_manager(member=None):
    member = create_member() if member is None else member
    return Manager.objects.create(member=member)

class PresidentModelTests(TestCase):
    def create_all(self):
        self.manager = create_manager()

    def test_null_profile(self):
        self.create_all()
        president = President(assos_id=self.manager.assos_id, profile_id=None)
        with self.assertRaises(IntegrityError): #see comment below
            president.save()

    def test_null_assos(self):
        self.create_all()
        president = President(assos_id=None, profile_id=self.manager.profile_id)
        with self.assertRaises(IntegrityError): #If I full_clean doesnt raise ValidationError but RelatedObjectDoesntExist instead
            president.save()

    def test_null_manager(self):
        president = President(manager=None)
        with self.assertRaises(IntegrityError): #see comment above
            president.save()

    def test_valid_input(self):
        self.create_all()
        president = President(assos_id=self.manager.assos_id,
                          profile_id=self.manager.profile_id)
        self.assertTrue(isinstance(president, President))
        president.full_clean()
        president.save()

    def test_not_unique_compositeonetoonefield(self):
        self.create_all()
        President.objects.create(manager=self.manager)
        president = President(manager=self.manager)
        with self.assertRaises(ValidationError):
            president.full_clean()

    def test_no_ref_manager_profile_assos_combination(self):
        president = President(profile_id=create_profile("president"),
                          assos_id=create_association("president_assos"))
        with self.assertRaises(Manager.DoesNotExist):
            president.full_clean()

    def test_not_unique_assos(self):
        self.create_all()
        other_manager = create_manager(create_member(
                                       assos=self.manager.assos_id,
                                       profile=create_profile("new_profile")))
        President.objects.create(manager=self.manager)
        president = President(manager=other_manager)
        with self.assertRaises(ValidationError):
            president.full_clean()
"""    
    def test_unknown_profile(self):
    def test_unknow_assos(self):
"""

def create_date_time(days=0, hours=0):
    return timezone.now() + datetime.timedelta(days=days, hours=hours)

def make_event(title="event_title", state='P', manager=None,
                 assos=None, address=None, start=None, end=None, premium=False):
    manager = create_manager() if manager is None else manager
    assos = manager.assos_id if assos is None else assos
    address = create_address() if address is None else address
    start = create_date_time(days=1) if start is None else start
    end = start + datetime.timedelta(hours=5) if end is None else end
    return Event(title=title, event_state=state,
                                manager_id=manager, assos_id=assos,
                                address_id=address, start=start, end=end,
                                premium_flag=premium)

def create_event(title="event_title", state='P', manager=None,
                 assos=None, address=None, start=None, end=None, premium=False):
    return make_event(title, state, manager, assos, address, start,
                      end, premium).save();

class EventModelTests(TestCase):
    def test_too_long_title(self):
        with self.assertRaises(ValidationError):
            make_event(title="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
                    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").full_clean()

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
        event.full_clean()
        event.save()
""" 
    def test_unknown_manager_id(self):
    def test_unknown_assos_id(self):
    def test_unknown_address(self):


class TicketModelTests(TestCase):
    def test_invalid_ticket_type(slef):
    def test_unknown_event(self):
    def test_past_event(self):
    def test_refused_event(self):
    def test_pending_envent(self):
    def test_ongoing_event(self):
    def test_approved_event(self):
    def test_null_ticket_type(self):
    def test_null_event(self):


class PriceModelTests(TestCase):
    def test_invalid_ticket_type(self):
    def test_null_ticket_type(self):
    def test_unknown_event(self):
    def test_negative_price(self):
    def test_null_price(self):
    def test_null_event(self):
    def test_str(self):
    def test_not_unique_combination_type_event(self):
    def test_valid_input(self):


class  PurchaseModelTests(TestCase):
    def test_unknown_event(self):
    def test_null_event(self):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknown_ticket(self):
    def test_null_ticket(self):
    def test_non_corresponding_ticket_and_event(self):
    def test_non_unique_combination_ticket_event_profile(self):
    def test_valid_input(self):
"""
