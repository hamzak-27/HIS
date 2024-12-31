from django import forms
from .models import Patient, EmergencyContact, FamilyMember, Guarantor

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'birth_time': forms.TimeInput(attrs={'type': 'time'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'visa_expiry': forms.DateInput(attrs={'type': 'date'}),
        }

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        exclude = ['patient']

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        exclude = ['patient']

class GuarantorForm(forms.ModelForm):
    class Meta:
        model = Guarantor
        exclude = ['patient']


from django import forms
from .models import Doctor, Schedule, Appointment

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['doctor', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time")
        
        return cleaned_data

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient_name', 'doctor', 'schedule']

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        
        if schedule and not schedule.is_available:
            raise forms.ValidationError("This time slot is no longer available")
        
        return cleaned_data