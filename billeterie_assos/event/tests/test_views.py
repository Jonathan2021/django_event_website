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

# Should either assign perms directly or create an object with user that assign perms, idk what is better
#When creating and deleting, should maybe make a querysetequal assert before and after, not just after
# when testing not logged in etc. maybe test that nothing was deleted or created

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
        self.assertTemplateUsed(response, 'index.html')

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

    def test_two_future_events_ordering(self):
        ref = create_event(start=create_date_time(days=1), premium=True)
        future = deepcopy(ref)
        future.pk = None
        future.start = create_date_time(days=2)
        future.end = create_date_time(days=3)
        future.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                map(repr, [ref, future]))
        with self.assertRaises(AssertionError):
            self.assertQuerysetEqual(response.context['events'],
                                     map(repr, [future, ref]))

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
        self.assertTemplateUsed(response, 'event_list.html')



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

    def test_two_future_events_ordering(self):
        ref = create_event(start=create_date_time(days=1), premium=True)
        future = deepcopy(ref)
        future.pk = None
        future.start = create_date_time(days=2)
        future.end = create_date_time(days=3)
        future.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, future.title)
        self.assertQuerysetEqual(response.context['events'],
                                map(repr, [ref, future]))
        with self.assertRaises(AssertionError):
            self.assertQuerysetEqual(response.context['events'],
                                     map(repr, [future, ref]))

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
        self.assertContains(response, self.event.title)
        self.assertContains(response, self.event.assos_id.name)
        self.assertEqual(response.context['event'], self.event)
        self.assertTemplateUsed(response, 'event_detail.html')

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
    
    def test_get_success_url(self):
        request = RequestFactory().post('blabla')
        v = setup_view(views.EventCreateView(), request)
        event = create_event(assos=self.asso)
        v.object = event
        self.assertEqual(v.get_success_url(), reverse('event:event_detail', kwargs={'pk': event.pk}))

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
        self.assertTemplateUsed(response, 'event_new.html')


    def test_wrong_asso_pk(self):
        url = reverse('event:event_creation', kwargs={'asso' :  69})
        create_member(profile=self.user, assos=self.asso)
        self.client.force_login(self.user)
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 404)

    def test_creation_post(self):
        create_member(profile=self.user, assos=self.asso)
        self.client.force_login(self.user)
        form_data = {
                'title': 'test',
                'event_state': models.Event.PENDING,
                'manager_id': "",
                'start': '2019-12-25 14:30',
                'end': '2019-12-25 17:30',
                'assos_id': self.asso.pk,
                'address_id': "69 rue de la baise",
                'premium_flag': True,
                'intern_number': 0,
                'intern_price': 0,
                'extern_number': 0,
                'extern_price': 0,
                'staff_number': 0,
                'staff_price': 0
                }
        form = forms.CreateEventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        self.assertQuerysetEqual(models.Event.objects.all(), [])
        response = self.client.post(self.url, form_data)
        self.assertRedirects(response, reverse('event:event_detail',
                                               kwargs={'pk' : 1}))
        with self.assertRaises(AssertionError):
            self.assertQuerysetEqual(models.Event.objects.all(), [])
        event = models.Event.objects.get(pk=1)
        self.assertEquals(event.title, form_data['title'])

    def test_create_get(self):
        create_member(profile=self.user, assos=self.asso)
        self.client.force_login(self.user)
        form_data = {
                'title': 'test',
                'event_state': models.Event.PENDING,
                'manager_id': "",
                'start': '2019-12-25 14:30',
                'end': '2019-12-25 17:30',
                'assos_id': self.asso.pk,
                'address_id': "69 rue de la baise",
                'premium_flag': True,
                'intern_number': 0,
                'intern_price': 0,
                'extern_number': 0,
                'extern_price': 0,
                'staff_number': 0,
                'staff_price': 0
                }
        form = forms.CreateEventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        response = self.client.get(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(models.Event.objects.all(), [])
       
        

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
        form_data = {'users' : "bonjour"}
        form = forms.AddMemberForm(data=form_data, user=self.user, asso=self.asso)
        self.assertFalse(form.is_valid())
        request = RequestFactory().get(self.url, form_data)
        request.user = self.user
        self.v.request = request
        response = self.v.post(request) #is_bound attr of form is False since it s GET request -> form.is_valid returns false
        # should probably make it fail another way
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(models.Member.objects.filter(user__in=[user1, user2]), [])

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
        query_dict =  QueryDict('', mutable=True)
        query_dict.update({'users' : repr(user1.pk)})
        query_dict.update({'users' : repr(user2.pk)})
        self.v.request.POST = query_dict
        form  = forms.AddMemberForm(data=query_dict, asso=self.asso, user=self.user) 
        self.assertTrue(form.is_valid())
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
        self.assertTemplateUsed(response, 'assos_detail.html')

    def test_post_wrong_pk(self):
        response = self.client.post(reverse('event:asso_detail', kwargs={'pk' : 69}))
        self.assertEquals(response.status_code, 404)

    def test_correct_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, self.url)
        self.assertTemplateNotUsed(response, 'assos_detail.html')

    def test_form_with_get(self):
        user1 = create_user(name='user1')
        user2 = create_user(name='user2')
        form_data = {'users' : [user1.pk, user2.pk]}
        response = self.client.get(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(self.asso.members.filter(user__in=[user1, user2]), [])


class MyAssosViewTests(TestCase):
    def setUp(self):
        self.url = reverse('event:my_assos')
        self.user = create_user()
        self.asso = create_association(name="aaaa")
        self.member = create_member(assos=self.asso, profile=self.user)

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_no_assos(self):
        self.asso.delete()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['assos'], [])
        self.assertTemplateUsed(response, 'assos_list.html')

    def test_assos_but_no_memberships(self):
        self.member.delete()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['assos'], [])
        self.assertNotContains(response, self.asso.name)

    def test_memberships(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['assos'], [repr(self.asso)])
        self.assertContains(response, self.asso.name)

    def test_ordering(self):
        new_asso = create_association(name="bbbbb")
        create_member(assos=new_asso, profile=self.user)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['assos'],
                                 map(repr, [self.asso, new_asso]))
        with self.assertRaises(AssertionError):
            self.assertQuerysetEqual(response.context['assos'],
                                     map(repr, [new_asso, self.asso]))
        self.assertContains(response, self.asso.name)
        self.assertContains(response, new_asso.name)


class AssosViewTests(TestCase):
    def setUp(self):
        self.url = reverse('event:assos')
     
    def test_no_assos(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['assos'], [])
        self.assertTemplateUsed(response, 'assos_list.html')

    def test_assos_and_ordering(self):
        asso_1 = create_association(name="salut")
        asso_2 = create_association(name="toi")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertQuerysetEqual(response.context['assos'], map(repr, [asso_1, asso_2]))
        with self.assertRaises(AssertionError):
            self.assertQuerysetEqual(response.context['assos'], map(repr, [asso_2, asso_1]))
        self.assertContains(response, asso_1.name)
        self.assertContains(response, asso_2.name)


class AssosDeleteTests(TestCase):
    def setUp(self):
        self.asso = create_association()
        self.url = reverse('event:assos_delete', kwargs={'pk' : self.asso.pk})
        self.user = create_user()

    def test_get_success_url(self):
        request = RequestFactory().post('deleting')
        request.build_absolute_uri = lambda url : url
        avoid = reverse('event:asso_detail', kwargs={'pk' : self.asso.pk})
        meta = {'HTTP_REFERER' : avoid}
        request.META = meta
        v = setup_view(views.AssosDelete(), request)
        v.kwargs = {'pk' : self.asso.pk}
        self.assertEqual(v.get_success_url(), reverse('event:index'))
        assos = reverse('event:assos')
        request.META['HTTP_REFERER'] = assos
        self.assertEqual(v.get_success_url(), assos)
        request.META = {}
        self.assertEqual(v.get_success_url(), reverse('event:index'))



    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_but_no_delete_association_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 403)

    def test_wrong_pk(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('event:assos_delete', kwargs={'pk' : 69}))
        self.assertEquals(response.status_code, 404)


    def test_get(self):
        self.client.force_login(self.user)
        assign_perm('event.delete_association', self.user, self.asso)
        self.assertQuerysetEqual(models.Association.objects.all(), [repr(self.asso)])
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:index'))
        self.assertQuerysetEqual(models.Association.objects.all(), [])

    def test_post(self):
        self.client.force_login(self.user)
        assign_perm('event.delete_association', self.user, self.asso)
        self.assertQuerysetEqual(models.Association.objects.all(), [repr(self.asso)])
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('event:index'))
        self.assertQuerysetEqual(models.Association.objects.all(), [])


class MemberDeleteTests(TestCase):
    def setUp(self):
        self.asso = create_association()
        self.user = create_user()
        self.member = create_member(assos=self.asso, profile=self.user)
        self.url = reverse('event:delete_member',
                            kwargs={'pk' : self.member.pk,
                                    'asso_pk': self.asso.pk})
    
    def test_get_success_url(self):
        request = RequestFactory().get('wallah')
        v = setup_view(views.MemberDelete(), request, asso_pk=self.asso.pk)
        self.assertEquals(v.get_success_url(), reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_no_manage_members_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 403)

    def test_logged_in_with_perms(self):
        self.client.force_login(self.user)
        assign_perm('manage_member', self.user, self.asso)
        self.assertQuerysetEqual(self.asso.members.all(), [repr(self.member)])
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.members.all(), [])

    def test_wrong_pk(self):
        self.client.force_login(self.user)
        assign_perm('manage_member', self.user, self.asso)
        response = self.client.get(reverse('event:delete_member',
                                           kwargs={'pk': 69,
                                                   'asso_pk': self.asso.pk}))
        self.assertEquals(response.status_code, 404)

    def test_wrong_asso_pk(self):
        self.client.force_login(self.user)
        assign_perm('manage_member', self.user, self.asso)
        response = self.client.get(reverse('event:delete_member',
                                           kwargs={'pk': self.member.pk,
                                                   'asso_pk': 69}))
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user)
        assign_perm('manage_member', self.user, self.asso)
        self.assertQuerysetEqual(self.asso.members.all(), [repr(self.member)])
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.members.all(), [])

    def test_post(self):
        self.client.force_login(self.user)
        assign_perm('manage_member', self.user, self.asso)
        self.assertQuerysetEqual(self.asso.members.all(), [repr(self.member)])
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.members.all(), [])


class ManagerDeleteTests(TestCase):
    def setUp(self):
        self.asso = create_association()
        self.user = create_user()
        self.manager = create_manager(member=create_member(assos=self.asso, profile=self.user))
        self.url = reverse('event:delete_manager',
                            kwargs={'pk' : self.manager.pk,
                                    'asso_pk': self.asso.pk})
    def test_get_success_url(self):
        request = RequestFactory().get('wallah')
        v = setup_view(views.ManagerDelete(), request, asso_pk=self.asso.pk)
        self.assertEquals(v.get_success_url(), reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_no_manage_manager_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 403)

    def test_logged_in_with_perms(self):
        self.client.force_login(self.user)
        member = self.manager.member
        assign_perm('manage_manager', self.user, self.asso)
        self.assertQuerysetEqual(self.asso.managers.all(), [repr(self.manager)])
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), [])
        self.assertQuerysetEqual(self.asso.members.all(), [repr(member)])

    def test_wrong_pk(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.get(reverse('event:delete_manager',
                                           kwargs={'pk': 69,
                                                   'asso_pk': self.asso.pk}))
        self.assertEquals(response.status_code, 404)

    def test_wrong_asso_pk(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.get(reverse('event:delete_manager',
                                           kwargs={'pk': self.manager.pk,
                                                   'asso_pk': 69}))
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user)
        member = self.manager.member
        assign_perm('manage_manager', self.user, self.asso)
        self.assertQuerysetEqual(self.asso.managers.all(), [repr(self.manager)])
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), [])
        self.assertQuerysetEqual(self.asso.members.all(), [repr(member)])

    def test_post(self):
        self.client.force_login(self.user)
        member = self.manager.member
        assign_perm('manage_manager', self.user, self.asso)
        self.assertQuerysetEqual(self.asso.managers.all(), [repr(self.manager)])
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), [])
        self.assertQuerysetEqual(self.asso.members.all(), [repr(member)])


class ManagerCreateTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.asso = create_association()
        self.member = create_member(assos=self.asso, profile=self.user)
        self.url = reverse('event:add_manager', kwargs={'asso_pk' : self.asso.pk, 'pk' : self.member.pk})
    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_no_manage_manager_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 403)

    def test_logged_in_with_perms(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), map(repr, models.Manager.objects.filter(member=self.member))) # weird
        self.assertQuerysetEqual(self.asso.members.all(), [repr(self.member)])

    def test_wrong_member_pk(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.get(reverse('event:add_manager',
                                           kwargs={'pk': 69,
                                                   'asso_pk': self.asso.pk}))
        self.assertEquals(response.status_code, 404)

    def test_wrong_asso_pk(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.get(reverse('event:add_manager',
                                           kwargs={'pk': self.member.pk,
                                                   'asso_pk': 69}))
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), map(repr, models.Manager.objects.filter(member=self.member))) # weird how filter here is not repr
        self.assertQuerysetEqual(self.asso.members.all(), [repr(self.member)])

    def test_post(self):
        self.client.force_login(self.user)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), map(repr, models.Manager.objects.filter(member=self.member)))
        self.assertQuerysetEqual(self.asso.members.all(), [repr(self.member)])

    def test_already_manager(self):
        self.client.force_login(self.user)
        manager = create_manager(member=self.member)
        assign_perm('manage_manager', self.user, self.asso)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(), [repr(manager)])

class PresidentCreateTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.asso = create_association()
        self.manager = create_manager(member=create_member(assos=self.asso, profile=self.user))
        self.president = models.President.objects.create(manager=create_manager(member=create_member(profile=create_user(name="blabla"), assos=self.asso)))
        self.url = reverse('event:add_president', kwargs={'pk' : self.manager.pk})

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_no_add_president_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_with_perms(self):
        self.client.force_login(self.user)
        manager = self.president.manager
        self.assertEquals(self.asso.president, self.president)
        assign_perm('event.add_president', self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertEquals(models.President.objects.get(assos_id=self.asso).user, self.user)
        self.assertQuerysetEqual(self.asso.managers.all(),
                                      map(repr, [self.manager, manager]),
                                      ordered=False)

    def test_wrong_manager_pk(self):
        self.client.force_login(self.user)
        assign_perm('event.add_president', self.user)
        response = self.client.get(reverse('event:add_president',
                                           kwargs={'pk': 69}))
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user)
        pres_manager = self.president.manager
        assign_perm('event.add_president', self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(),
                                 map(repr, [self.manager, pres_manager]),
                                ordered=False)
        self.assertEquals(self.asso.president.user, self.user)
        self.assertQuerysetEqual(models.President.objects.filter(user=pres_manager.user), [])

    def test_post(self):
        self.client.force_login(self.user)
        pres_manager = self.president.manager
        assign_perm('event.add_president', self.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertQuerysetEqual(self.asso.managers.all(),
                                 map(repr, [self.manager, pres_manager]),
                                 ordered=False)
        self.assertEquals(self.asso.president.user, self.user)
        self.assertQuerysetEqual(models.President.objects.filter(user=pres_manager.user), [])

    def test_is_already_pres(self):
        self.client.force_login(self.user)
        assign_perm('event.add_president', self.user)
        self.president.delete()
        pres = models.President.objects.create(manager=self.manager)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertEqual(repr(self.asso.president), repr(pres))

    def test_pres_not_exist(self):
        self.client.force_login(self.user)
        assign_perm('event.add_president', self.user)
        self.president.delete()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk': self.asso.pk}))
        self.assertEqual(self.asso.president.user, self.manager.user)


class AssosCreateViewTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.name = 'test_asso'
        self.url = reverse('event:asso_creation')

    def test_get_success_url(self):
        request = RequestFactory().post('post')
        v = setup_view(views.AssosCreateView(), request)
        asso = create_association()
        v.object = asso
        self.assertEquals(v.get_success_url(),  reverse('event:asso_detail', kwargs={'pk' : asso.pk}))

    def test_form_valid(self):
        form_data = {
                'name' : self.name,
                'president' : self.user.pk
                }
        form = forms.AssociationForm(data=form_data)
        self.assertTrue(form.is_valid())
        request = RequestFactory().post('post')
        v = setup_view(views.AssosCreateView(), request)
        v.form_valid(form)
        asso = models.Association.objects.all().first()
        self.assertEqual(asso.name, self.name)
        self.assertEqual(asso.president.user, self.user)
        self.assertQuerysetEqual(asso.members.all(), map(repr, self.user.memberships.all()))
        self.assertQuerysetEqual(asso.managers.all(), map(repr, self.user.managerships.all()))
        
    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)

    def test_logged_in_no_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)
    
    def test_logged_in_with_perms_post(self):
        self.client.force_login(self.user)
        assign_perm('event.add_association', self.user)
        form_data = {
                'name' : self.name,
                'president' : self.user.pk
                }
        form = forms.AssociationForm(data=form_data)
        self.assertTrue(form.is_valid())
        response = self.client.post(self.url, form_data)
        asso = models.Association.objects.all().first()
        self.assertEqual(asso.name, self.name)
        self.assertEqual(asso.president.user, self.user)
        self.assertQuerysetEqual(asso.members.all(), map(repr, self.user.memberships.all()))
        self.assertQuerysetEqual(asso.managers.all(), map(repr, self.user.managerships.all()))
        self.assertRedirects(response, reverse('event:asso_detail', kwargs={'pk' : asso.pk}))

    def test_post_invalid_form(self):
        self.client.force_login(self.user)
        assign_perm('event.add_association', self.user)
        form_data = {
                'name' : self.name,
                'president' : 64
                }
        form = forms.AssociationForm(data=form_data)
        self.assertFalse(form.is_valid())
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        self.client.force_login(self.user)
        assign_perm('event.add_association', self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'association_new.html')
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_perms_get(self):
        self.client.force_login(self.user)
        assign_perm('event.add_association', self.user)
        form_data = {
                'name' : self.name,
                'president' : self.user.pk
                }
        form = forms.AssociationForm(data=form_data)
        self.assertTrue(form.is_valid())
        response = self.client.get(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(models.Association.objects.all(), [])

class EventDeleteTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.asso = create_association()
        self.event = create_event(assos=self.asso)
        self.url = reverse('event:event_delete', kwargs={'pk' : self.event.pk})

    def test_get_success_url(self):
        request = RequestFactory().post('deleting')
        request.build_absolute_uri = lambda url : url
        avoid = reverse('event:event_detail', kwargs={'pk' : self.event.pk})
        meta = {'HTTP_REFERER' : avoid}
        request.META = meta
        v = setup_view(views.EventDelete(), request)
        v.kwargs = {'pk' : self.event.pk}
        self.assertEqual(v.get_success_url(), reverse('event:index'))
        events = reverse('event:events')
        request.META['HTTP_REFERER'] = events
        self.assertEqual(v.get_success_url(), events)
        request.META = {}
        self.assertEqual(v.get_success_url(), reverse('event:index'))


    def test_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = reverse('login') + '?next=' + urllib.parse.quote(self.url, "")
        self.assertRedirects(response, expected_url)
        self.assertQuerysetEqual(models.Event.objects.all(), [repr(self.event)])

    def test_logged_in_no_delete_event_perms(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(models.Event.objects.all(), [repr(self.event)])

    def test_get_with_perms(self):
        assign_perm('event.delete_event', self.user, self.event)
        self.client.force_login(self.user)
        self.assertQuerysetEqual(models.Event.objects.all(), [repr(self.event)])
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('event:index'))
        self.assertQuerysetEqual(models.Event.objects.all(), [])

    def test_wrong_pk(self):
        assign_perm('event.delete_event', self.user, self.event)
        self.client.force_login(self.user)
        response = self.client.get(reverse('event:event_delete', kwargs={'pk' : 69}))
        self.assertEqual(response.status_code, 404)

    def test_post_with_perms(self):
        assign_perm('event.delete_event', self.user, self.event)
        self.client.force_login(self.user)
        self.assertQuerysetEqual(models.Event.objects.all(), [repr(self.event)])
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('event:index'))
        self.assertQuerysetEqual(models.Event.objects.all(), [])
