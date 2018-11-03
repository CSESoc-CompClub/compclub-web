import datetime
import re

from django import forms
from django.forms import (DateInput, DateTimeInput, Form, ModelForm, TimeInput,
                          ValidationError)
from django.utils.translation import gettext_lazy as _

from website.models import Event, Registration, VolunteerAssignment, Workshop


class DatePicker(DateInput):
    input_type = 'date'


class DateTimePicker(DateTimeInput):
    input_type = 'datetime-local'


class TimePicker(TimeInput):
    input_type = 'time'


class EventForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # adding ".form-control" class to all fields so that they are styled by
        # bootstrap.css
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Event
        fields = '__all__'
        exclude = ('slug', )
        help_texts = {
            'start_date':
            _('First day of the event'),
            'finish_date':
            _('Last day of the event, cannot be earlier than start date'),
            'owner':
            _('Person who manages this event'),
        }
        widgets = {
            'start_date': DatePicker(),
            'finish_date': DatePicker(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        finish_date = cleaned_data.get('finish_date')
        if all([start_date, finish_date]) and start_date > finish_date:
            raise ValidationError(
                _('Finish date cannot be earlier than start date %(start_date)s > %(finish_date)s'
                  ),
                code='invalid date',
                params={
                    'start_date': start_date,
                    'finish_date': finish_date
                })


class WorkshopForm(ModelForm):
    REPEAT_CHOICES = (('NO', 'None'), ('DL', 'Daily'), ('WK', 'Weekly'))
    repeat_workshop = forms.ChoiceField(choices=REPEAT_CHOICES)

    def __init__(self, *args, **kwargs):
        super(WorkshopForm, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Workshop
        fields = ('event', 'start_time', 'end_time', 'date', 'name',
                  'location', 'repeat_workshop')
        exclude = ()
        help_texts = {'time': _('Must be in Sydney time')}
        widgets = {
            'event': forms.HiddenInput(),
            'start_time': TimePicker,
            'end_time': TimePicker,
            'date': DatePicker
        }

    def make_recurring_workshops(self, interval):
        """
        Create recurring workshops
        interval: datetime.timedelta object
        """
        cleaned_data = self.cleaned_data
        current_date = cleaned_data.get('date') + interval
        while current_date <= cleaned_data.get('event').finish_date:
            Workshop.objects.create(
                event=cleaned_data.get('event'),
                name=cleaned_data.get('name'),
                date=current_date,
                start_time=cleaned_data.get('start_time'),
                end_time=cleaned_data.get('end_time'),
                description=cleaned_data.get('description'),
                location=cleaned_data.get('location'))
            current_date += interval

    def clean(self):
        cleaned_data = super().clean()
        workshop_date = cleaned_data.get('date')
        event = cleaned_data.get('event')
        if event is None:
            raise ValidationError(_('No event provided'), code='null event')

        if workshop_date is None:
            raise ValidationError(
                _('Invalid workshop date entered'), code='invalid date')

        if workshop_date > event.finish_date or workshop_date < event.start_date:
            raise ValidationError(
                _('Workshop date cannot be earlier or later than the event dates'),
                code='invalid date')

        if cleaned_data.get('start_time') is None:
            raise ValidationError(
                _('Invalid workshop start time entered'), code='invalid time')

        if cleaned_data.get('end_time') is None:
            raise ValidationError(
                _('Invalid workshop start time entered'), code='invalid time')

        if cleaned_data.get('start_time') > cleaned_data.get('end_time'):
            raise ValidationError(
                _('Workshop start time cannot be later than the end time'),
                code='invalid time')

    def save(self):
        super().save()
        recurrence = self.cleaned_data['repeat_workshop']
        if recurrence == 'DL':
            self.make_recurring_workshops(datetime.timedelta(days=1))
        elif recurrence == 'WK':
            self.make_recurring_workshops(datetime.timedelta(days=7))


class RegistrationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Registration
        fields = '__all__'
        widgets = {
            'date_of_birth': DatePicker,
            'event': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        number = cleaned_data['number']
        parent_number = cleaned_data['parent_number']
        pattern = r'\d{8,}'
        if (re.search(pattern, number) is None
                or re.search(pattern, parent_number) is None):
            raise ValidationError(
                _('Phone number is invalid. Must be at least 8 characters long.'),
                code='invalid number')


class VolunteerAssignForm(Form):
    '''Form for assigning available volunteers to a workshop'''
    workshop_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        # Get available volunteers
        available = kwargs.pop('available')
        # Get existing VolunteerAssignments for that workshop
        assignments = kwargs.pop('assignments')
        super(VolunteerAssignForm, self).__init__(*args, **kwargs)

        # add each available volunteer as a radio ChoiceField
        for v in available:
            user = v.user
            try:
                # get current assignment for volunteer
                status = assignments.get(volunteer=v).status
                self.fields[f'vol_{v.id}'] = forms.ChoiceField(
                    widget=forms.RadioSelect(),
                    choices=VolunteerAssignment.ASSIGN_CHOICES,
                    initial=status,
                    label=f'{user.first_name} {user.last_name} ({user.email})')
            except VolunteerAssignment.DoesNotExist:
                self.fields[f'vol_{v.id}'] = forms.ChoiceField(
                    widget=forms.RadioSelect(),
                    choices=VolunteerAssignment.ASSIGN_CHOICES,
                    label=f'{user.first_name} {user.last_name} ({user.email})')

    # Yields collection of assignments received from the form.
    def get_assignments(self):
        for field, value in self.cleaned_data.items():
            if field.startswith('vol_'):
                yield (field[4], value)

    # Saves assignment into model
    def save(self):
        for vol_id, status in self.get_assignments():
            VolunteerAssignment.objects.update_or_create(
                workshop_id=self.cleaned_data['workshop_id'],
                volunteer_id=vol_id,
                defaults={'status': status})
