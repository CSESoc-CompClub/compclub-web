import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime

from website import models
from website.forms import EventForm, VolunteerAssignForm, WorkshopForm
from website.models import CustomUser, VolunteerAssignment, Workshop
from website.utils import generate_status_email

from .management.commands.load_dummy_data import make_event

# make_event() arguments for adding test event
singular_event_args = {
    'name': 'Intro to Programming Crash Course',
    'days_from_now': 10,
    'n_week': 1,
    'workshop_time': datetime.time(10, 0),  # 10:00 local time
    'description': 'Have you ever wanted to learn to write computer programs?',
    'prereq': 'No programming experience required',
    'period': '???',
    'location': 'UNSW k17 oud lab',
}

multi_workshop_event_args = {
    'name':
    'Test: Advanced Web Development',
    'days_from_now':
    28,
    'n_week':
    7,
    'workshop_time':
    datetime.time(16, 0),
    'description':
    'Learn how to make full-scale web apps with Django',
    'prereq':
    'Experience in web design (HTML,CSS,JavaScript) and coding in Python',
    'period':
    '2 hours',
    'location':
    'UNSW K17 lyre lab'
}


class EventIndexViewTests(TestCase):
    def setUp(self):
        self.skipTest('redirects to homepage')

    def test_no_events(self):
        '''if there are no events, an appropriate message is displayed'''
        response = self.client.get(reverse('website:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There aren't any events at this time")
        self.assertQuerysetEqual(response.context['events_list'], [])

    def test_past_event(self):
        '''Past event should not be displayed'''
        past_event_args = dict(singular_event_args)
        past_event_args['days_from_now'] = -2
        make_event(**past_event_args)

        response = self.client.get(reverse('website:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There aren't any events at this time")
        self.assertQuerysetEqual(response.context['events_list'], [])

    def test_single_event(self):
        '''test event with single workshop'''
        event = make_event(**singular_event_args)
        response = self.client.get(reverse('website:index'))
        local_start = localtime(event.start_date)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 1)
        self.assertContains(response, event.name)
        self.assertNotContains(response, ' Workshops') # n Workshops
        self.assertContains(response, local_start.strftime('%b')) # month
        self.assertContains(response, local_start.strftime('%d')) # day

    def test_recurring_event(self):
        '''test event with multiple workshops'''
        event = make_event(**multi_workshop_event_args)
        response = self.client.get(reverse('website:index'))

        local_start = localtime(event.start_date)
        local_finish = localtime(event.finish_date)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 1)
        self.assertContains(response, event.name)
        self.assertContains(response, ' Workshops')  # n Workshops
        self.assertContains(response, event.start_date.strftime('%b'))  # month
        self.assertContains(response, event.start_date.strftime('%d'))  # day
        self.assertContains(response, event.finish_date.strftime('%b'))
        self.assertContains(response, event.finish_date.strftime('%d'))

    def test_multiple_events(self):
        event1 = make_event(**multi_workshop_event_args)
        event2 = make_event(**singular_event_args)
        response = self.client.get(reverse('website:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 2)
        self.assertContains(response, event1.name)
        self.assertContains(response, event2.name)

    def test_current_recurring_event(self):
        ''' should show multi-workshop event that has some but not all of its
            workshops in the past
        '''
        event_args = dict(multi_workshop_event_args)
        event_args['days_from_now'] = -7
        event_args['n_week'] = 3
        event = make_event(**event_args)

        response = self.client.get(reverse('website:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 1)
        self.assertContains(response, event.name)


class EventFormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.owner = models.CustomUser.objects.create_superuser(
            username='su', email='', password='1234')

    def test_event_create_valid(self):
        form_data = {
            'name': 'Intro to Python',
            'start_date': '2018-01-01',
            'finish_date': '2018-04-30',
            'event_types': 'UIE',
            'owner': '1',
            'description': 'introduction to Python',
            'prerequisite': 'Nil',
            'period': 'period',
            'slug': 'Intro-to-Python'
        }
        form = EventForm(data=form_data)
        form.is_valid()
        print(form.errors)
        self.assertTrue(form.is_valid())


    def test_event_create_invalid_dates(self):
        form_data = {
            'name': 'Intro to Python',
            'start_date': '2018-04-30',
            'finish_date': '2018-04-29',
            'owner': '1',
            'description': 'introduction to Python',
            'prerequisite': 'Nil',
            'period': 'period',
            'slug': 'Intro-to-Python'
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_event_create_invalid_name(self):
        form_data = {
            'name':
            'Name that exceeds 100 characters.........................'
            '................................................................',
            'start_date':
            '2018-04-30',
            'finish_date':
            '2018-04-29',
            'owner':
            '1',
            'description':
            'introduction to Python',
            'prerequisite':
            'Php :)',
            'period':
            'period',
            'slug':
            'Name-that-exceeds-100-characters.........................'
            '................................................................',
        }
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())


class WorkshopFormTest(TestCase):
    def setUp(self):
        form_data = {
            'name': 'Intro to Python',
            'start_date': '2018-10-31',
            'finish_date': '2018-11-08',
            'owner': '1',
            'event_types':'UE',
            'description': 'introduction to Python',
            'prerequisite': 'Nil',
            'period': 'period',
            'slug': 'Intro-to-Python'
        }
        self.owner = CustomUser.objects.create_superuser(
            username='su', email='', password='1234')
        self.event = EventForm(data=form_data).save()

    def test_workshop_create_valid(self):
        form_data = {
            'event': '1',
            'name': 'workshop name',
            'date': '2018-10-31',
            'start_time': '22:59',
            'end_time': '23:59',
            'location': 'k17 seminar room',
            'repeat_workshop': 'NO'
        }
        form = WorkshopForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_workshop_create_invalid_name(self):
        form_data = {
            'event': '1',
            'name': 'long name................................................'
                '................................................................',
            'date': '2018-10-31',
            'start_time': '22:59',
            'end_time': '23:59',
            'location': 'k17 seminar room',
            'repeat_workshop': 'NO'
        }
        form = WorkshopForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_workshop_create_invalid_time(self):
        form_data = {
            'event': '1',
            'name': 'workshop name',
            'date': '2018-10-32',
            'start_time': '22:59',
            'end_time': '23:59',
            'location': 'k17 seminar room',
            'repeat_workshop': 'NO'
        }
        form = WorkshopForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_workshop_create_no_recurring(self):
        form_data = {
            'event': '1',
            'name': 'workshop name',
            'date': '2018-10-31',
            'start_time': '22:59',
            'end_time': '23:59',
            'location': 'k17 seminar room',
            'repeat_workshop': 'NO'
        }
        form = WorkshopForm(data=form_data)
        form.save()
        self.assertTrue(len(Workshop.objects.all()) == 1)

    def test_workshop_create_recurring_daily(self):
        form_data = {
            'event': '1',
            'name': 'workshop name',
            'date': '2018-10-31',
            'start_time': '22:59',
            'end_time': '23:59',
            'location': 'k17 seminar room',
            'repeat_workshop': 'DL'
        }
        form = WorkshopForm(data=form_data)
        form.save()
        self.assertTrue(len(Workshop.objects.all()) == 9) # 8 days inclusive between 31/10 and 8/11

    def test_workshop_create_recurring_weekly(self):
        form_data = {
            'event': '1',
            'name': 'workshop name',
            'date': '2018-11-01',
            'start_time': '22:59',
            'end_time': '23:59',
            'location': 'k17 seminar room',
            'repeat_workshop': 'WK'
        }
        form = WorkshopForm(data=form_data)
        form.save()
        self.assertTrue(len(Workshop.objects.all()) == 2)


class EventCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.su = models.CustomUser.objects.create_superuser(
            username='su', email='', password='1234')

    def test_call_view_denies_non_staff(self):
        expected_redirect_url = f"{reverse('admin:login')}?next={reverse('website:event_create')}"
        response = self.client.get(
            reverse('website:event_create'), follow=True)
        self.assertRedirects(response, expected_redirect_url)
        response = self.client.post(
            reverse('website:event_create'), follow=True)
        self.assertRedirects(response, expected_redirect_url)

    def test_call_view_loads(self):
        self.client.login(username='su', password='1234')
        response = self.client.get(reverse('website:event_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/event_create.html')


class VolunteerAssignmentModelTest(TestCase):
    ''' tests for VolunteerAssignment model '''

    def setUp(self):
        '''Volunteer assignment'''
        # create event with 1 workshop
        self.event = make_event(**singular_event_args)
        self.workshop = Workshop.objects.filter(event=self.event)[0]

        # create volunteers Alice and Bob
        user_alice = CustomUser.objects.create_user(
            username='alice', email='', password='1234')
        user_bob = CustomUser.objects.create_user(
            username='bob', email='', password='1234')
        self.alice = user_alice.volunteer
        self.bob = user_bob.volunteer

        # both available for workshop
        self.workshop.available.add(self.alice)
        self.workshop.available.add(self.bob)

        # only Alice is assigned, Bob is on waitlist
        VolunteerAssignment.objects.create(
            workshop=self.workshop,
            volunteer=self.alice,
            status=VolunteerAssignment.ASSIGNED
        )
        VolunteerAssignment.objects.create(
            workshop=self.workshop,
            volunteer=self.bob,
            status=VolunteerAssignment.WAITLIST
        )


    def test_available(self):
        '''Check that both Alice and Bob are available for workshop'''
        self.assertIn(self.alice, self.workshop.available.all())
        self.assertIn(self.bob, self.workshop.available.all())
        self.assertEqual(self.alice.workshops_available.first(), self.workshop)
        self.assertEqual(self.bob.workshops_available.first(), self.workshop)

    def test_assigned(self):
        '''Check that Alice and Bob are assigned correctly'''
        self.assertIn(self.alice, self.workshop.assigned.all())
        self.assertIn(self.bob, self.workshop.assigned.all())
        self.assertEqual(self.alice.workshops_assigned.first(), self.workshop)
        self.assertEqual(self.bob.workshops_assigned.first(), self.workshop)
        self.assertEqual(len(self.workshop.assignment.all()), 2)
        self.assertEqual(self.alice.assignment.first().status, VolunteerAssignment.ASSIGNED)
        self.assertEqual(self.bob.assignment.first().status, VolunteerAssignment.WAITLIST)

    def test_form_valid(self):
        '''Test Assignment form with valid data'''
        data = {
            'workshop_id': self.workshop.id,
            f'vol_{self.alice.id}': VolunteerAssignment.ASSIGNED,
            f'vol_{self.bob.id}': VolunteerAssignment.WAITLIST
        }
        form = VolunteerAssignForm(
            data,
            available=self.workshop.available.all(),
            assignments=self.workshop.assignment.all())
        self.assertTrue(form.is_valid)

    def test_view(self):
        '''Test assigning view called correctly'''
        CustomUser.objects.create_superuser(
            username='su', email='', password='1234')
        self.client.login(username='su', password='1234')
        response = self.client.get(reverse(
            'website:assign_volunteers', args=[self.event.slug,self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'website/event_assign.html')
