from django.test import TestCase
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone
from django.utils import timezone
# from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile, EmailAddress
from address.models import Address

# Create your tests here.


def create_date(days):
    return timezone.now() + datetime.timedelta(days=days)


class ProfileModelTests(TestCase):

    def create_user(self, name='test', mail='test@test.com',\
            passw='S_8472QLqdqd7+'):
        self.user = User(username=name, email=mail, password=passw)

    def create_address(self):
        self.address = Address(raw='11 rue du Vert Buisson')
    
    def create_profile(self, gender=True, birthdate=create_date(-1)):
        self.profile = Profile(user=self.user, gender=gender,  birth_date=birthdate,
                address_id=self.address)
  
    def create_all(self):
        self.create_user()
        self.create_address()
        self.create_profile()

    def test_null_user(self):
        self.create_address()
        self.create_user()
        self.create_profile()
        with self.assertRaises(ValidationError):
            self.profile.full_clean()
    
    def test_with_correct_input(self):
        self.create_all()
        self.assertTrue(isinstance(self.profile, Profile))

    def test_future_birth_date(self):
        self.create_user()
        self.create_address()
        self.create_profile(birthdate=create_date(1))
        with self.assertRaises(ValidationError):
            self.profile.full_clean()
 
    def test_null_gender(self):
        self.create_user()
        self.create_address()
        self.create_profile(gender=None)
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_null_birth_date(self):
        self.create_user()
        self.create_address()
        self.create_profile(birthdate=None)
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_profile_str(self):
        self.create_all()
        self.assertIs(self.profile.__str__() == ('%s (%s)' %\
                (self.user.get_full_name(), self.user.email)), True)

"""
class EmailAddressModelTests(TestCase):

    def create_email(self, email='test@test.com')
        self.email = email

    def test_invalid_email(self):

    def test_not_unique_email(self):
    def test_valid_input(self):
    def test_unknown_profile(self):
    def test_null_email(self):
    def test_null_profile(self):
    def test_profile_cascade(self):


class AssociationModelTests(TestCase):
    def test_too_long_name(self):
    def test_blank_name(self):
    def test_null_name(self):
    def test_not_unique_name(self):
    def test_str(self):


class MemberModelTests(TestCase):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknow_assos(self):
    def test_null_assos(self):
    def test_not_unique_combination_profile_assos(self):
    def test_valid_input(self):

 
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
