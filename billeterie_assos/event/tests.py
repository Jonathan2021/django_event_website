from django.test import TestCase
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone
from django.db.utils import IntegrityError
# from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile, Association, Member
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


def create_profile():
    return Profile.objects.create(user=create_user(), gender=True,
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

def create_association():
    return Association.objects.create(name="assos_test")


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

""" 
class ManagerModelTests(TestCase):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknow_assos(self):
    def test_null_assos(self):
    def test_not_unique_combination_profile_assos(self):
    def test_valid_input(self):
    def test_no_ref_member_profile_assos_combination(self):


class PresidentModelTests(TestCase):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknow_assos(self):
    def test_null_assos(self):
    def test_not_unique_combination_profile_assos(self):
    def test_not_unique_assos(self):
    def test_valid_input(self):
    def test_no_ref_member_profile_assos_combination(self):

        
class EventModelTests(TestCase):
    def test_too_long_title(self):
    def test_invalid_event_state(self):
    def test_unknown_manager_id(self):
    def test_null_title(self):
    def test_null_event_state(self):
    def test_unknown_assos_id(self):
    def test_unknown_address(self):
    def test_null_manager_id(self):
    def test_null_assos_id(self):
    def test_start_after_end(self):
    def test_start_and_end_at_same_time(self):
    def test_null_start(self):
    def test_null_end(self):
    def test_null_premium_flag(self):
    def test_valid_input(self):
    def test_finished_before_end(self):


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
