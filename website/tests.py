from django.test import TestCase
from django.urls import reverse

from website.forms import EventForm, WorkshopForm
from website.models import CustomUser


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
