from django.forms import DateInput, DateTimeInput, ModelForm, ValidationError
from website.models import Registration
from django.utils.translation import gettext_lazy as _

class DatePicker(DateInput):
    input_type = 'date'

class DateTimePicker(DateTimeInput):
    input_type= 'datetime-local'

class RegistrationForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)

    class Meta:
        model = Registration
        fields = '__all__'
        exclude = ()
        
    def clean(self):
        cleaned_dae = super().clean()
