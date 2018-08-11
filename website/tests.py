import datetime
from django.test import TestCase
from django.urls import reverse
from website.forms import EventForm, WorkshopForm
from website.models import CustomUser
from .management.commands.load_dummy_data import make_event

# make_event() arguments for adding test event
singular_event_args = {
    'name': 'Intro to Programming Crash Course',
    'days_from_now': 10,
    'n_week': 1,
    'workshop_time': datetime.time(10, 0), # 10:00 local time
    'description': 'Have you ever wanted to learn to write computer programs?',
    'prereq': 'No programming experience required',
    'period': '???',
    'location': 'UNSW k17 oud lab',
}

multi_workshop_event_args = {
    'name': 'Test: Advanced Web Development',
    'days_from_now': 28,
    'n_week': 7,
    'workshop_time': datetime.time(16, 0),
    'description': 'Learn how to make full-scale web apps with Django',
    'prereq': 'Experience in web design (HTML,CSS,JavaScript) and coding in Python',
    'period': '2 hours',
    'location': 'UNSW K17 lyre lab'
}

class EventIndexViewTests(TestCase):
    def test_no_events(self):
        '''if there are no events, an appropriate message is displayed'''
        response = self.client.get(reverse('website:event_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There aren't any events at this time")
        self.assertQuerysetEqual(response.context['events_list'], [])
    
    def test_past_event(self):
        '''Past event should not be displayed'''
        past_event_args = dict(singular_event_args)
        past_event_args['days_from_now'] = -2
        make_event(**past_event_args)

        response = self.client.get(reverse('website:event_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There aren't any events at this time")
        self.assertQuerysetEqual(response.context['events_list'], [])
    
    def test_single_event(self):
        '''test event with single workshop'''
        self.skipTest('until utc/local timezone in browser is fixed')
        event = make_event(**singular_event_args)
        response = self.client.get(reverse('website:event_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 1)
        self.assertContains(response, event.name)
        self.assertNotContains(response, ' Workshops') # n Workshops
        self.assertContains(response, event.start_date.strftime('%b')) # month
        self.assertContains(response, event.start_date.strftime('%d')) # day

    def test_recurring_event(self):
        '''test event with multiple workshops'''
        self.skipTest('until utc/local timezone in browser is fixed')
        event = make_event(**multi_workshop_event_args)
        response = self.client.get(reverse('website:event_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 1)
        self.assertContains(response, event.name)
        self.assertContains(response, ' Workshops') # n Workshops
        self.assertContains(response, event.start_date.strftime('%b')) # month
        self.assertContains(response, event.start_date.strftime('%d')) # day
        self.assertContains(response, event.finish_date.strftime('%b'))
        self.assertContains(response, event.finish_date.strftime('%d'))
    
    def test_multiple_events(self):
        event1 = make_event(**multi_workshop_event_args)
        event2 = make_event(**singular_event_args)
        response = self.client.get(reverse('website:event_index'))
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

        response = self.client.get(reverse('website:event_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['events_list']), 1)
        self.assertContains(response, event.name)




class EventFormTest(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_superuser(
            username='su', email='', password='1234')

    def test_event_create_valid(self):
        form_data = {
            'name': 'Intro to Python',
            'start_date': '2018-01-01',
            'finish_date': '2018-04-30',
            'owner': '1',
            'description': 'introduction to Python',
            'prerequisite': 'Nil',
            'period': 'period',
            'slug': 'Intro-to-Python'
        }
        form = EventForm(data=form_data)
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
    def test_workshop_create_valid(self):
        form_data = {
            'name': 'workshop name',
            'time': '2018-10-31 23:59',
            'description': 'workshop description',
            'location': 'k17 seminar room'
        }
        form = WorkshopForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_workshop_create_invalid_name(self):
        form_data = {
            'name':
            'long name................................................'
            '................................................................',
            'time':
            '2018-10-31 23:59',
            'description':
            'workshop description',
            'location':
            'k17 seminar room'
        }
        form = WorkshopForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_workshop_create_invalid_time(self):
        form_data = {
            'name': 'workshop name',
            'time': '2018-10-32 12:34',
            'description': 'workshop description',
            'location': 'k17 seminar room'
        }
        form = WorkshopForm(data=form_data)
        self.assertFalse(form.is_valid())


class EventCreateViewTest(TestCase):
    def setUp(self):
        self.su = CustomUser.objects.create_superuser(
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
