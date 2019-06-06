from django.urls import reverse
from django.test import TestCase, RequestFactory, TransactionTestCase
from django_downloadview.test import setup_view
from .test_models import create_event, create_date_time, create_user, \
    create_association, create_member
from event import models
from event import views
from copy import deepcopy
from django.contrib.auth.models import AnonymousUser
import urllib

class IndexViewTests(TestCase):
    def test_get_queryset(self):
        request = RequestFactory().get('/request/mabite')
        v = setup_view(views.IndexView(), request)
        v.get_queryset()

    def test_no_event(self):
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No Premium event")
        self.assertQuerysetEqual(response.context['events'], [])

    def test_no_premium(self):
        create_event(premium=False)
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No Premium event")
        self.assertQuerysetEqual(response.context['events'], [])

    def test_past_premium_event(self):
        create_event(start=create_date_time(days=-1), premium=True)
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No Premium event")
        self.assertQuerysetEqual(response.context['events'], []) 

    def test_future_premium_event(self):
        event = create_event(start=create_date_time(days=1), premium=True)
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, event.title)
        self.assertQuerysetEqual(response.context['events'],
                                [repr(event)])
        

    def test_past_and_future(self):
        past = create_event(start=create_date_time(days=-1), premium=True)
        future = deepcopy(past)
        future.start = create_date_time(days=1)
        future.end = create_date_time(days=1)
        future.pk = None
        future.save()
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                [repr(future)])

    def test_two_future_events(self):
        ref = create_event(start=create_date_time(days=1), premium=True)
        future = deepcopy(ref)
        future.pk = None
        future.save()
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                map(repr, [ref, future]), ordered=False)

    def test_on_going_event(self):
        create_event(start=create_date_time(days=-1), end=create_date_time(days=1))
        response = self.client.get(reverse('event:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, No event)
        self.assertQuerysetEqual(response.context['events'], [])


class EventListView(TestCase):
    def test_get_queryset(self):
        request = RequestFactory().get('/request/machatte')
        v = setup_view(views.EventListView(), request)
        v.get_queryset()


    def test_no_event(self):
        response = self.client.get(reverse('event:events'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, No event)
        self.assertQuerysetEqual(response.context['events'], [])



    def test_past_event(self):
        event = create_event(start=create_date_time(days=-1))
        response = self.client.get(reverse('event:events'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No event")
        self.assertQuerysetEqual(response.context['events'], []) 



    def test_future_event(self):
        event = create_event(start=create_date_time(days=1))
        response = self.client.get(reverse('event:events'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, event.title)
        self.assertQuerysetEqual(response.context['events'], [repr(event)]) 



    def test_past_and_future(self):
        past = create_event(start=create_date_time(days=-1))
        future = deepcopy(past)
        future.start = create_date_time(days=1)
        future.end = create_date_time(days=1)
        future.pk = None
        future.save()
        response = self.client.get(reverse('event:events'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                [repr(future)])

    def test_on_going_event(self):
        event = create_event(start=create_date_time(days=-1), end=create_date_time(days=1))
        response = self.client.get(reverse('event:events'))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, No event)
        self.assertQuerysetEqual(response.context['events'], [repr(event)])


class EventDetailViewTests(TestCase):
    def test_invalid_pk(self):
        response = self.client.get(reverse('event:event_detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 404)

    def test_valid_complete(self):
        event = create_event()
        response = self.client.get(reverse('event:event_detail', kwargs={'pk' : event.pk}))
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, event.title)
        # self.assertContains(response, event.assos_id.name)
        # self.assertContains(response, event.address_id.raw)
        # etc.
        self.assertEqual(response.context['event'], event)

    def test_no_manager(self):
        event = create_event()
        response = self.client.get(reverse('event:event_detail', kwargs={'pk' : event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No manager")
        # self.assertContains(response, event.assos_id.name)
        # self.assertContains(response, event.address_id.raw)
        # etc.
        self.assertEqual(response.context['event'], event)




class EventCreateViewTests(TransactionTestCase):
    def setUp(self):
        super(EventCreateViewTests, self).setUp()
        self.user = create_user()
        self.asso = create_association()
        self.url = reverse('event:event_creation', kwargs={'asso' : self.asso.pk })

    def test_not_logged_in(self):
        response = self.client.get(self.url, follow=True)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)


    def test_user_not_member(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 403)

    def test_user_is_member(self):
        create_member(profile=self.user, assos=self.asso) 
        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 200)


    def test_wrong_asso_pk(self):
        url = reverse('event:event_creation', kwargs={'asso' :  69})
        create_member(profile=self.user, assos=self.asso) 
        self.client.force_login(self.user)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 404)


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
