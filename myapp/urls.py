from django.urls import path
from . import views 

app_name = 'appointments'

urlpatterns = [
    path('', views.home, name="home"),
    path('registration/', views.registration, name="registration"),
    path('registration/patient_registration/', views.patient_registration, name="patient_registration"),
    path('patients/', views.patient_list, name='patient_list'),
    path('process-emirates-id/', views.process_emirates_id, name='process_emirates_id'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('schedule/manage/', views.doctor_schedule_view, name='manage_schedule'),
    path('appointment/book/', views.appointment_booking_view, name='book_appointment'),
    path('api/available-slots/<int:doctor_id>/<str:date>/', views.get_available_slots, name='get_available_slots'),
    path('api/schedule/events/', views.get_schedule_events, name='schedule_events'),
]
