from django.urls import reverse
from django.test import TestCase

class IndexViewTests(TestCase):
    def test_no_event(self):
        pass

    def test_no_premium(self):
        pass

    def test_past_event(self):
        pass

    def test_future_event(self):
        pass

    def test_past_and_future(self):
        pass

    def test_get(self):
        pass


class EventListView(TestCase):
    def test_no_event(self):
        pass

    def test_past_event(self):
        pass

    def test_future_event(self):
        pass

    def test_past_and_future(self):
        pass


class EventDetailViewTests(TestCase):
    def test_invalid_pk(self):
        pass

    def test_valid_pk(self):
        pass


class EventCreateViewTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user(self):
        pass

    def test_anonymous_user_is_member(self):
        pass

    def test_user_not_member(self):
        pass

    def test_user_is_member(self):
        pass

    def test_wrong_asso_pk(self):
        pass


class AssosDetailView(TestCase):
    def test_get_wrong_pk(self):
        pass

    def test_no_president(self): # should maybe raise an error idk
        pass

    def test_no_manager(self):
        pass

    def test_no_member(self):
        pass

    def test_president_only(self):
        pass

    def test_president_and_managers(self):
        pass # should test if president not in manager displayed

    def test_president_and_members(self):
        pass

    def test_managers_and_members(self):
        pass

    def test_pres_managers_and_members(self):
        pass

    def test_post_wrong_pk(self):
        pass
    
    def test_correct_post(self):
        pass

class MyAssosViewTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_logged_in(self):
        pass

    def test_logged_in(self):
        pass

    def test_no_assos(self):
        pass

    def test_assos_but_no_memberships(self):
        pass

    def test_memberships(self):
        pass

    def test_ordering(self):
        pass

class AssosViewTests(TestCase):
    def test_no_assos(self):
        pass

    def test_assos(self):
        pass

    def test_ordering(self):
        pass


class AssosDeleteTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user(self):
        pass

    def test_logged_in_but_no_delete_association_perms(self):
        pass

    def test_wrong_pk(self):
        pass

    def test_get(self):
        pass

    def test_post(self):
        pass

class MemberDeleteTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user_no_perms(self):
        pass
    
    def test_anonymous_user_with_perms(self):
        pass

    def test_logged_in_no_manage_members_perms(self):
        pass

    def test_logged_in_with_perms(self):
        pass

    def test_wrong_pk(self):
        pass
   
    def test_wrong_asso_pk(self):
        pass

    def test_get(self):
        pass

    def test_post(self):
        pass

class ManagerDeleteTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user_no_perms(self):
        pass
    
    def test_anonymous_user_with_perms(self):
        pass

    def test_logged_in_no_manage_manager_perms(self):
        pass

    def test_logged_in_with_perms(self):
        pass

    def test_wrong_pk(self):
        pass
   
    def test_wrong_asso_pk(self):
        pass

    def test_get(self):
        pass

    def test_post(self):
        pass


def ManagerCreateTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user_no_perms(self):
        pass
    
    def test_anonymous_user_with_perms(self):
        pass

    def test_logged_in_no_manage_manager_perms(self):
        pass

    def test_logged_in_with_perms(self):
        pass

    def test_wrong_member_pk(self):
        pass

    def test_member_not_saved(self): # should be tested in model tests
        pass
   
    def test_wrong_asso_pk(self):
        pass

    def test_get(self):
        pass

    def test_post(self):
        pass


class PresidentCreateTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user_no_perms(self):
        pass
    
    def test_anonymous_user_with_perms(self):
        pass

    def test_logged_in_no_manage_president_perms(self):
        pass

    def test_logged_in_with_perms(self):
        pass

    def test_wrong_manager_pk(self):
        pass

    def test_manager_not_saved(self): # should be tested in model tests
        pass
   
    def test_wrong_asso_pk(self):
        pass

    def test_get(self):
        pass

    def test_post(self):
        pass

class AssosCreateViewTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user_no_perms(self):
        pass
    
    def test_anonymous_user_with_perms(self):
        pass

    def test_logged_in_no_add_association_perms(self):
        pass

    def test_logged_in_with_perms(self):
        pass

    def test_no_users(self):
        pass

    def test_user_not_saved(self): # should be tested in model tests
        pass
   
    def test_get(self):
        pass

    def test_post(self):
        pass


class EventDeleteTests(TestCase):
    def test_not_logged_in(self):
        pass

    def test_anonymous_user_no_perms(self):
        pass
    
    def test_anonymous_user_with_perms(self):
        pass

    def test_logged_in_no_delete_event_perms(self):
        pass

    def test_logged_in_with_perms(self):
        pass

    def test_wrong_pk(self):
        pass

    def test_event_not_saved(self): # should be tested in model tests
        pass
   
    def test_get(self):
        pass

    def test_post(self):
        pass
