from django.contrib import admin
from .models import Patient, EmergencyContact, FamilyMember, Guarantor

# Register your models here.
admin.site.register(Patient)
admin.site.register(EmergencyContact)
admin.site.register(FamilyMember)
admin.site.register(Guarantor)


from .models import Doctor, Schedule, Appointment



from django.contrib import admin
from .models import Doctor, Schedule, Appointment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name', 'department')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('doctor', 'date', 'is_available')
    search_fields = ('doctor__name',)
    date_hierarchy = 'date'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'schedule', 'status', 'created_at')
    list_filter = ('status', 'doctor', 'schedule__date')
    search_fields = ('patient_name', 'doctor__name')
    date_hierarchy = 'created_at'