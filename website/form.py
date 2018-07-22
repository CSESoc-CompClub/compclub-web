from django.forms import DateInput, DateTimeInput, ModelForm, ValidationError
from website.models import Registration

class DatePicker(DateInput):
    input_type = 'date'

class DateTimePicker(DateTimeInput):
    input_type= 'datetime-local'

class RegistrationForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)

    class Meta:
        model = Registration
        field = ['name','email','number','date_of_birth','parent_email','parent_number']
    
    def clean(self):
        cleaned_dae = super().clean()
