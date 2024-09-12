from django import forms
from .models import Consultation
from django.core.exceptions import ValidationError

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = '__all__'  # Include all fields from the model