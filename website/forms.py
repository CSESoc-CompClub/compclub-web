from django.forms import DateInput, DateTimeInput, ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _

from website.models import Event, Workshop


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
        exclude = ('event', )
        help_texts = {'time': _('Must be in Sydney time')}
        widgets = {
            'time': DateTimePicker(),
        }
