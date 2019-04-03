from django.test import TestCase

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

# Create your tests here.

"
def create_date(days):
    return timezone.now() + datetime.timedelta(days=days)


def ProfileModelTests(TestCase):
    def test_non_existent_user(self):
    def test_null_user(self):
    def test_with_correct_input(self):
    def test_future_birth_date(self):
    def test_null_gender(self):
    def test_null_birth_date(self):
    def test_destroying_user(self):
    def test_profile_str(self):


def EmailAddressModelTests(TestCase):
    def test_invalid_email(self):
    def test_not_unique_email(self):
    def test_valid_input(self):
    def test_unknown_profile(self):
    def test_null_email(self):
    def test_null_profile(self):
    def test_profile_cascade(self):


def AssociationModelTests(TestCase):
    def test_too_long_name(self):
    def test_blank_name(self):
    def test_null_name(self):
    def test_not_unique_name(self):
    def test_str(self):


def MemberModelTests(TestCase):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknow_assos(self):
    def test_null_assos(self):
    def test_not_unique_combination_profile_assos(self):
    def test_valid_input(self):

 
def ManagerModelTests(TestCase):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknow_assos(self):
    def test_null_assos(self):
    def test_not_unique_combination_profile_assos(self):
    def test_valid_input(self):
    def test_no_ref_member_profile_assos_combination(self):


def PresidentModelTests(TestCase):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknow_assos(self):
    def test_null_assos(self):
    def test_not_unique_combination_profile_assos(self):
    def test_not_unique_assos(self):
    def test_valid_input(self):
    def test_no_ref_member_profile_assos_combination(self):

        
def EventModelTests(TestCase):
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


def TicketModelTests(TestCase):
    def test_invalid_ticket_type(slef):
    def test_unknown_event(self):
    def test_past_event(self):
    def test_refused_event(self):
    def test_pending_envent(self):
    def test_ongoing_event(self):
    def test_approved_event(self):
    def test_null_ticket_type(self):
    def test_null_event(self):


def PriceModelTests(TestCase):
    def test_invalid_ticket_type(self):
    def test_null_ticket_type(self):
    def test_unknown_event(self):
    def test_negative_price(self):
    def test_null_price(self):
    def test_null_event(self):
    def test_str(self):
    def test_not_unique_combination_type_event(self):
    def test_valid_input(self):


def PurchaseModelTests(TestCase):
    def test_unknown_event(self):
    def test_null_event(self):
    def test_unknown_profile(self):
    def test_null_profile(self):
    def test_unknown_ticket(self):
    def test_null_ticket(self):
    def test_non_corresponding_ticket_and_event(self):
    def test_non_unique_combination_ticket_event_profile(self):
    def test_valid_input(self):
"
