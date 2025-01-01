from django.db import models

# Create your models here.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Patient(models.Model):
    TITLE_CHOICES = [
        ('MR', 'Mr'),
        ('MS', 'Ms'),
        ('MRS', 'Mrs'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Basic Information (Form 1)
    title = models.CharField(max_length=3, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    patient_phone = models.CharField(max_length=20)
    patient_email = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField()
    age = models.CharField(max_length=4, blank=True)
    birth_time = models.CharField(max_length=10)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    patient_id = models.CharField(max_length=20, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    
    # Address (Form 2)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # Visa Details (Form 3)
    visa_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    visa_type = models.CharField(max_length=50, blank=True, null=True)
    visa_expiry = models.DateField(blank=True, null=True)
    
    # Insurance (Form 4)
    insurance_name = models.CharField(max_length=100, blank=True, null=True)
    insurance_plan = models.CharField(max_length=100, blank=True, null=True)
    insurance_benefits = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.display_name} ({self.patient_id})"

class EmergencyContact(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=100, blank=True, null=True)

class FamilyMember(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    contact = models.CharField(max_length=20)

class Guarantor(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='guarantors')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    contact = models.CharField(max_length=20)
    address = models.TextField()
