from django.forms import DateInput, DateTimeInput, ModelForm, ValidationError
from website.models import Registration
from django.utils.translation import gettext_lazy as _
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
        exclude = ()
        widgets = {
            'date_of_birth': DatePicker,
            
        }

    def clean(self):
        data = self.cleaned_dat
        number = data.get("number")
        pemail = data.get("parent_email")
        pnumber = data.get("parent_number")
        pattern = "\A04[\d{8}]|\A02[\d{8}]"
        if((re.search(pattern,number)==None) or (re.search(pattern,pnumber)==None)):
            raise ValueError("invalid number")
