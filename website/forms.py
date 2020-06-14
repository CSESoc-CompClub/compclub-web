"""Django forms for compclub website."""

import datetime
import re

from django import forms
from django.forms import (DateInput, Form, ModelForm, TimeInput,
                          ValidationError)
from django.utils.translation import gettext_lazy as _

from website.models import (CustomUser, Event, Registration, Student,
                            VolunteerAssignment, Workshop)

from django.contrib.auth.password_validation import validate_password


class DatePicker(DateInput):
    """DatePicker Form Field. Used to select a date in a form."""

    input_type = 'date'


class TimePicker(TimeInput):
    """TimePicker Form Field. Used to select a time in a form."""

    input_type = 'time'


class EventForm(ModelForm):
    """Event creation form. Creates a new Event model object upon saving."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super(EventForm, self).__init__(*args, **kwargs)
        # adding ".form-control" class to all fields so that they are styled by
        # bootstrap.css
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:  # noqa: D106
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
        """Clean and validate the form data."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        finish_date = cleaned_data.get('finish_date')
        if all([start_date, finish_date]) and start_date > finish_date:
            raise ValidationError(_('Finish date cannot be earlier than start'
                                    ' date %(start_date)s > %(finish_date)s'),
                                  code='invalid date',
                                  params={
                                      'start_date': start_date,
                                      'finish_date': finish_date
            })


class WorkshopForm(ModelForm):
    """
    Workshop creation form.

    Creates one or more workshops for a specific event upon saving.
    """

    REPEAT_CHOICES = (('NO', 'None'), ('DL', 'Daily'), ('WK', 'Weekly'))
    repeat_workshop = forms.ChoiceField(choices=REPEAT_CHOICES)

    def __init__(self, *args, **kwargs):  # noqa: D107
        super(WorkshopForm, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:  # noqa: D106
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
        Create recurring workshops.

        Args:
            interval: datetime.timedelta object. The time interval between each
                      workshop

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
                location=cleaned_data.get('location'))
            current_date += interval

    def clean(self):
        """Clean and validate the form data."""
        cleaned_data = super().clean()
        workshop_date = cleaned_data.get('date')
        event = cleaned_data.get('event')
        if event is None:
            raise ValidationError(_('No event provided'), code='null event')

        if workshop_date is None:
            raise ValidationError(_('Invalid workshop date entered'),
                                  code='invalid date')

        if (workshop_date > event.finish_date
                or workshop_date < event.start_date):
            raise ValidationError(_(
                'Workshop date cannot be earlier or later than the event dates'
            ),
                code='invalid date')

        if cleaned_data.get('start_time') is None:
            raise ValidationError(_('Invalid workshop start time entered'),
                                  code='invalid time')

        if cleaned_data.get('end_time') is None:
            raise ValidationError(_('Invalid workshop start time entered'),
                                  code='invalid time')

        if cleaned_data.get('start_time') > cleaned_data.get('end_time'):
            raise ValidationError(
                _('Workshop start time cannot be later than the end time'),
                code='invalid time')

    def save(self):
        """Create an object model and save it to the database."""
        super().save()
        recurrence = self.cleaned_data['repeat_workshop']
        if recurrence == 'DL':
            self.make_recurring_workshops(datetime.timedelta(days=1))
        elif recurrence == 'WK':
            self.make_recurring_workshops(datetime.timedelta(days=7))


class CreateUserForm(ModelForm):
    """Create a new user."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super(CreateUserForm, self).__init__(*args, **kwargs)
        # adding ".form-control" class to all fields so that they are styled by
        # bootstrap.css
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_("Enter the same password as above."))

    class Meta:  # noqa: D106
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(
                attrs={
                    'autocomplete': 'family-name'}),
            'username': forms.TextInput(
                attrs={
                    'autocomplete': 'username'}),
            'email': forms.EmailInput(
                attrs={
                    'autocomplete': 'email'}),
            'password': forms.PasswordInput(
                attrs={
                    'autocomplete': 'new-password'})}
        help_texts = {
            'email': 'An email that you will regularly check.',
            'username': 'The name you will sign in with.'}
        validators = {
            'password': validate_password
        }

    def clean_password2(self):
        """Validate passwords match."""
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        """Save a new user."""
        user = super(CreateUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CreateStudentForm(ModelForm):
    """Create a student model."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super(CreateStudentForm, self).__init__(*args, **kwargs)
        # adding ".form-control" class to all fields so that they are styled by
        # bootstrap.css
        for field in self:
            if field.field.widget.attrs.get('class', None):
                field.field.widget.attrs['class'] += ' form-control'
            else:
                field.field.widget.attrs['class'] = 'form-control'

    class Meta:  # noqa: D106
        model = Student
        exclude = ('user',)

        help_texts = {
            'school': (
                'If you are home schooled put Home School. ' +
                'If your school isn\'t in the list put Other.')}

        widgets = {
            'school': forms.Select(
                attrs={
                    'class': 'selectpicker form-control',
                    'data-live-search': 'true',
                    'data-size': '5'}
            ),
        }

        labels = {
            'email_consent': (
                'I agree to be sent email related to CompClub ' +
                'using my provided email.')
        }

    def clean_email_consent(self):
        """Require email consent."""
        email_consent = self.cleaned_data.get("email_consent")
        if not email_consent:
            raise forms.ValidationError(
                'You must agree to receive emails from CompClub.')

        return email_consent


class RegistrationForm(ModelForm):
    """
    Student event registration form.

    Creates a new Registration object upon saving.
    """

    def __init__(self, *args, **kwargs):  # noqa: D107
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:  # noqa: D106
        model = Registration
        fields = '__all__'
        widgets = {
            'date_of_birth': DatePicker,
            'event': forms.HiddenInput(),
        }

    def clean(self):
        """Check if phone numbers are at least 8 characters long."""
        cleaned_data = super().clean()
        number = cleaned_data['number']
        parent_number = cleaned_data['parent_number']
        pattern = r'\d{8,}'
        if (re.search(pattern, number) is None
                or re.search(pattern, parent_number) is None):
            raise ValidationError(_(
                'Phone number is invalid. Must be at least 8 characters long.'
            ),
                code='invalid number')


class VolunteerAssignForm(Form):
    """Form for assigning available volunteers to a workshop."""

    workshop_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        """
        Initialise the volunteer assignment form.

        Args:
            *args:
                available: List of available volunteers (Django models)
                assignments: List of volunteer assignments (Django models)

        """
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

    def get_assignments(self):
        """Yield collection of assignments received from the form."""
        for field, value in self.cleaned_data.items():
            if field.startswith('vol_'):
                yield (field[4], value)

    def save(self):
        """Save assignment into model."""
        for vol_id, status in self.get_assignments():
            VolunteerAssignment.objects.update_or_create(
                workshop_id=self.cleaned_data['workshop_id'],
                volunteer_id=vol_id,
                defaults={'status': status})
