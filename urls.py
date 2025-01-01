from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name="home"),
    path('registration/', views.registration, name="registration"),
    path('registration/patient_registration/', views.patient_registration, name="patient_registration"),
    path('patients/', views.patient_list, name='patient_list'),
    path('process-emirates-id/', views.process_emirates_id, name='process_emirates_id'),
    path('patient/<str:patient_id>/pdf/', views.generate_patient_pdf, name='patient_pdf'),
]