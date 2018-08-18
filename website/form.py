from django.forms import DateInput, DateTimeInput, ModelForm, ValidationError,HiddenInput
from website.models import Registration
from django.utils.translation import gettext_lazy as _
from django import forms
import re

class DatePicker(DateInput):
    input_type = 'date'

class DateTimePicker(DateTimeInput):
    input_type= 'datetime-local'

class RegistrationForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Registration
        fields = '__all__'
        widgets = {
            'date_of_birth': DatePicker,
            'event' : forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        # print(cleaned_data)
        number = cleaned_data['number'] 
        pnumber = cleaned_data['parent_number'] 
        pattern = "\d{8,}"
        if((re.search(pattern,number)==None) or (re.search(pattern,pnumber)==None)):
            raise ValueError("invalid number")
