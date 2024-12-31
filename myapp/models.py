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
    display_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    birth_time = models.TimeField()
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    patient_id = models.CharField(max_length=20, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    
    # Address (Form 2)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    # Visa Details (Form 3)
    visa_number = models.CharField(max_length=50, blank=True, null=True)
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
    
    def calculate_age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        return age

class EmergencyContact(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

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

from django.db import models

# In myapp/models.py (add these to your existing models)

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} - {self.department}"

class Schedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.doctor.name} - {self.date} ({self.start_time} to {self.end_time})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed')
    ]
    
    patient_name = models.CharField(max_length=100)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} - {self.schedule.date}"