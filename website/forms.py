from django.forms import DateInput, DateTimeInput, ModelForm, ValidationError, Form
from django.utils.translation import gettext_lazy as _
from django import forms
from website.models import Event, Workshop, Registration, VolunteerAssignment
import re


class DatePicker(DateInput):
    input_type = 'date'


class DateTimePicker(DateTimeInput):
    input_type = 'datetime-local'


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
    def __init__(self, *args, **kwargs):
        super(WorkshopForm, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Workshop
        fields = '__all__'
        exclude = ('event', 'available', 'assigned')
        help_texts = {'time': _('Must be in Sydney time')}
        widgets = {
            'time': DateTimePicker(),
        }


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
                    label=f'{user.first_name} {user.last_name} ({user.email})'
                )
            except:
                self.fields[f'vol_{v.id}'] = forms.ChoiceField(
                    widget=forms.RadioSelect(),
                    choices=VolunteerAssignment.ASSIGN_CHOICES,
                    label=f'{user.first_name} {user.last_name} ({user.email})'
                )

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
                defaults={'status': status}
            )
