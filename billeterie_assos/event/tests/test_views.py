from django.urls import reverse
from django.test import TestCase, RequestFactory, TransactionTestCase, Client
from django_downloadview.test import setup_view
from .test_models import create_event, create_date_time, create_user, \
    create_association, create_member, create_manager
from event import models, views, forms
from copy import deepcopy
from django.contrib.auth.models import User, Permission
import urllib
from django.http import QueryDict
from guardian.shortcuts import assign_perm

# Do some assertTemplateUsed

class IndexViewTests(TestCase):
    def setUp(self):
        self.url = reverse('event:index')

    def test_get_queryset(self):
        request = RequestFactory().get('/request/mabite')
        v = setup_view(views.IndexView(), request)
        v.get_queryset()

    def test_no_event(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No Premium event")
        self.assertQuerysetEqual(response.context['events'], [])

    def test_no_premium(self):
        create_event(premium=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No Premium event")
        self.assertQuerysetEqual(response.context['events'], [])

    def test_past_premium_event(self):
        create_event(start=create_date_time(days=-1), premium=True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No Premium event")
        self.assertQuerysetEqual(response.context['events'], []) 

    def test_future_premium_event(self):
        event = create_event(start=create_date_time(days=1), premium=True)
        response = self.client.get(self.url)
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                [repr(future)])

    def test_two_future_events(self):
        ref = create_event(start=create_date_time(days=1), premium=True)
        future = deepcopy(ref)
        future.pk = None
        future.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                map(repr, [ref, future]), ordered=False)

    def test_on_going_event(self):
        create_event(start=create_date_time(days=-1), end=create_date_time(days=1))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, No event)
        self.assertQuerysetEqual(response.context['events'], [])


class EventListView(TestCase):
    def setUp(self):
        self.url = reverse('event:events')

    def test_get_queryset(self):
        request = RequestFactory().get('/request/machatte')
        v = setup_view(views.EventListView(), request)
        v.get_queryset()


    def test_no_event(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, No event)
        self.assertQuerysetEqual(response.context['events'], [])



    def test_past_event(self):
        create_event(start=create_date_time(days=-1))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, "No event")
        self.assertQuerysetEqual(response.context['events'], []) 



    def test_future_event(self):
        event = create_event(start=create_date_time(days=1))
        response = self.client.get(self.url)
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                [repr(future)])

    def test_on_going_event(self):
        event = create_event(start=create_date_time(days=-1), end=create_date_time(days=1))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, No event)
        self.assertQuerysetEqual(response.context['events'], [repr(event)])

    def test_no_delete_perms(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Delete')

    def test_with_delete_perms(self):
        event = create_event()
        user = create_user()
        self.client.force_login(user)
        assign_perm('event.delete_event', user, event)
        response = self.client.get(self.url)
        self.assertContains(response, 'Delete')


class EventDetailViewTests(TestCase):
    def setUp(self):
        self.event = create_event()
        self.url = reverse('event:event_detail', kwargs={'pk': self.event.pk})
    def test_invalid_pk(self):
        response = self.client.get(reverse('event:event_detail', kwargs={'pk': 69}))
        self.assertEqual(response.status_code, 404)

    def test_valid_complete(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, event.title)
        # self.assertContains(response, event.assos_id.name)
        # self.assertContains(response, event.address_id.raw)
        # etc.
        self.assertEqual(response.context['event'], self.event)

    def test_no_manager(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No manager")
        # self.assertContains(response, event.assos_id.name)
        # self.assertContains(response, event.address_id.raw)
        # etc.
        self.assertEqual(response.context['event'], self.event)

    def test_no_delete_perms(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Delete')

    def test_with_delete_perms(self):
        user = create_user()
        self.client.force_login(user)
        assign_perm('event.delete_event', user, self.event)
        response = self.client.get(self.url)
        self.assertContains(response, 'Delete')





class EventCreateViewTests(TransactionTestCase):
    def setUp(self):
        super(EventCreateViewTests, self).setUp()
        self.user = create_user()
        self.asso = create_association()
        self.url = reverse('event:event_creation', kwargs={'asso' : self.asso.pk })

    def test_get_form_kwargs(self):
        request = RequestFactory().get('/bonjour/toi')
        request.user = self.user
        self.client.force_login(self.user)
        create_member(profile=self.user, assos=self.asso)
        v = setup_view(views.EventCreateView(), request, asso=self.asso.pk)
        v.get_form_kwargs()



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
    def setUp(self):
        super(AssosDetailView, self).setUp()
        self.user = create_user()
        self.asso = create_association()
        self.url = reverse('event:asso_detail', kwargs={'pk' : self.asso.pk})
        request = RequestFactory().get('/dummy/lol')
        request.user = self.user
        self.v = setup_view(views.AssosDetailView(), request, pk=self.asso.pk)
        self.v.object = self.asso
        jo = create_user(name='jo')
        fred = create_user(name='fred')
        avrel = create_user(name='avrel')
        self.member = create_member(profile=jo, assos=self.asso)
        self.manager = create_manager(member=create_member(profile=fred,
                                                      assos=self.asso))
        self.president = models.President.objects.create(
                manager=create_manager(
                    member=create_member(
                            profile=avrel, assos=self.asso)))
        

    def test_get_object(self):
        res = self.v.get_object()
        self.assertEquals(res, self.asso)

    def test_get_form_kwargs(self):
        kwargs = self.v.get_form_kwargs()
        self.assertTrue(kwargs.get('user', None) is not None)
        self.assertTrue(kwargs.pop('asso', None) is not None)

    def test_get_success_url(self):
        url = self.v.get_success_url()
        self.assertEquals(url, reverse('event:asso_detail', kwargs={'pk' : self.asso.pk}))

    def test_get_context_data(self, **kwargs):
        context = self.v.get_context_data()
        future = create_event(assos=self.asso)
        create_event(assos=self.asso, start=create_date_time(days=-20))
        ongoing = create_event(assos=self.asso,
                                   start=create_date_time(days=-1),
                                   end=create_date_time(days=1))
        self.assertEquals(context['president'], self.president)
        self.assertQuerysetEqual(context['managers'], [repr(self.manager)])
        self.assertQuerysetEqual(context['members'], [repr(self.member)])
        self.assertQuerysetEqual(context['future_events'], [repr(future)])
        self.assertQuerysetEqual(context['ongoing_events'], [repr(ongoing)])
    
    def test_post_invalid_form(self):
        user1 = create_user(name='user1')
        user2 = create_user(name='user2')
        form_data = {'users' : [user1.pk, user2.pk]}
        request = RequestFactory().get(self.url, form_data)
        request.user = self.user
        self.v.request = request
        response = self.v.post(request) #is_bound attr of form is False since it s GET request -> form.is_valid returns false
        # should probably make it fail another way
        self.assertEquals(response.status_code, 200)

    def test_post_valid_form(self):
        user1 = create_user(name='user1')
        user2 = create_user(name='user2')
        form_data = {'users' : [user1.pk, user2.pk]}
        request = RequestFactory().post(self.url, form_data)
        request.user = self.user
        self.v.request = request
        response = self.v.post(request)
        response.client = Client()
        self.assertRedirects(response, self.url)
        self.assertNotEquals(models.Member.objects.filter(user__in=[user1, user2]), [])



    def test_form_valid(self):
        user1 = create_user(name='user1')
        user2 = create_user(name='user2')
        form  = forms.AddMemberForm(asso=self.asso, user=self.user) 
        query_dict =  QueryDict('', mutable=True)
        query_dict.update({'users' : repr(user1.pk)})
        query_dict.update({'users' : repr(user2.pk)})
        self.v.request.POST = query_dict
        self.v.form_valid(form)

    def test_get_wrong_pk(self):
        response = self.client.get(reverse('event:asso_detail', kwargs={'pk': 69}))
        self.assertEquals(response.status_code, 404)

    def test_no_president_in_context(self): # should maybe raise an error idk
        manager = self.president.manager
        self.president.delete()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertIs(response.context['president'], None)
        self.assertQuerysetEqual(response.context['managers'],
                                 map(repr, [self.manager, manager]),
                                 ordered=False)
        self.assertQuerysetEqual(response.context['members'], [repr(self.member)])

    def test_no_manager_in_context(self):
        member = self.manager.member
        self.manager.delete()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['president'], self.president)
        self.assertQuerysetEqual(response.context['managers'], [])
        self.assertQuerysetEqual(response.context['members'] , map(repr, [self.member, member]), ordered=False)

    def test_no_member_in_context(self):
        self.member.delete()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['president'], self.president)
        self.assertQuerysetEqual(response.context['managers'], [repr(self.manager)])
        self.assertQuerysetEqual(response.context['members'] , []) 

    def test_president_only(self):
        member = self.manager.member
        self.manager.delete()
        member.delete()
        self.member.delete()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['president'], self.president)
        self.assertQuerysetEqual(response.context['managers'], [])
        self.assertQuerysetEqual(response.context['members'] , []) 

    def test_pres_managers_and_members(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['president'], self.president)
        self.assertQuerysetEqual(response.context['managers'], [repr(self.manager)])
        self.assertQuerysetEqual(response.context['members'] , [repr(self.member)]) 

    def test_post_wrong_pk(self):
        response = self.client.post(reverse('event:asso_detail', kwargs={'pk' : 69}))
        self.assertEquals(response.status_code, 404)

    def test_correct_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.url)


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
