from django.core.validators import RegexValidator, MaxLengthValidator
from django.db import models


# Create your models here.
phone_validator = RegexValidator(
    regex=r'^\+91\d{10}$|^\d{10}$',
    message='Enter a valid Indian phone number with 10 digits or include country code +91.'
)

class Consultation(models.Model):
    clinic_name = models.CharField(max_length=200)
    clinic_logo = models.ImageField(upload_to='clinic_logos/')  # Store uploaded logos
    physician_name = models.CharField(max_length=200)
    physician_contact = models.CharField(
        max_length=13,  # Allow for optional country code
        validators=[phone_validator]  # Apply phone number validation
    )
    patient_first_name = models.CharField(max_length=200)
    patient_last_name = models.CharField(max_length=200)
    patient_dob = models.DateField()  # Use DateField for date of birth
    patient_contact = models.CharField(
        max_length=13,  # Allow for optional country code
        validators=[phone_validator]  # Apply phone number validation
    )
    chief_complaint = models.TextField(validators=[MaxLengthValidator(5000)])
    consultation_note = models.TextField(validators=[MaxLengthValidator(5000)])

    def __str__(self):
        return f"Consultation with {self.patient_first_name} {self.patient_last_name}"



