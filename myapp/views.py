from django.shortcuts import render, HttpResponse, redirect 
from django.contrib import messages
from .models import Patient
from .forms import (
    PatientRegistrationForm, EmergencyContactForm,
    FamilyMemberForm, GuarantorForm
)
from .utils import EmiratesIDProcessor
import json
from django.http import JsonResponse
from django.conf import settings

def home(request):
    return HttpResponse('Login/Register Page')

def registration(request):
    return render(request, 'index.html')

'''def patient_registration(request):
    return render(request, 'patient_registration.html')'''

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PatientRegistrationForm, EmergencyContactForm, FamilyMemberForm, GuarantorForm

def patient_registration(request):
    if request.method == 'POST':
        try:
            # Create form instances with submitted data
            patient_form = PatientRegistrationForm(request.POST)
            emergency_form = EmergencyContactForm(request.POST)
            family_form = FamilyMemberForm(request.POST)
            guarantor_form = GuarantorForm(request.POST)

            # Check if all forms are valid
            if all([
                patient_form.is_valid(),
                emergency_form.is_valid(),
                family_form.is_valid(),
                guarantor_form.is_valid()
            ]):
                # Save patient first
                patient = patient_form.save()

                # Save emergency contact with patient reference
                emergency_contact = emergency_form.save(commit=False)
                emergency_contact.patient = patient
                emergency_contact.save()

                # Save family member with patient reference
                family_member = family_form.save(commit=False)
                family_member.patient = patient
                family_member.save()

                # Save guarantor with patient reference
                guarantor = guarantor_form.save(commit=False)
                guarantor.patient = patient
                guarantor.save()

                messages.success(request, 'Patient registered successfully!')
                return redirect('patient_list')  # Redirect to patient list page
            else:
                messages.error(request, 'Please correct the errors in the form.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        # Create empty forms for GET request
        patient_form = PatientRegistrationForm()
        emergency_form = EmergencyContactForm()
        family_form = FamilyMemberForm()
        guarantor_form = GuarantorForm()

    # Render the template with forms
    return render(request, 'patient_registration.html', {
        'patient_form': patient_form,
        'emergency_form': emergency_form,
        'family_form': family_form,
        'guarantor_form': guarantor_form,
    })

def patient_list(request):
    patients = Patient.objects.all().order_by('-issue_date')
    return render(request, 'patient_list.html', {
        'patients': patients
    })

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .utils import EmiratesIDProcessor
import json

def process_emirates_id(request):
    if request.method == 'POST' and request.FILES.get('emirates_front') and request.FILES.get('emirates_back'):
        try:
            # Debug prints
            print("Files received:")
            print(f"Front file: {request.FILES['emirates_front'].name}")
            print(f"Back file: {request.FILES['emirates_back'].name}")
            print(f"Front file size: {request.FILES['emirates_front'].size}")
            print(f"Back file size: {request.FILES['emirates_back'].size}")

            processor = EmiratesIDProcessor(
                aws_access_key=settings.AWS_ACCESS_KEY,
                aws_secret_key=settings.AWS_SECRET_KEY,
                aws_region=settings.AWS_REGION,
                bucket_name=settings.AWS_BUCKET_NAME,
                openai_key=settings.OPENAI_API_KEY
            )

            front_file = request.FILES['emirates_front']
            back_file = request.FILES['emirates_back']

            try:
                extracted_data = processor.extract_emirates_data(front_file, back_file)
                
                if not extracted_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'No data could be extracted from the Emirates ID'
                    })

                return JsonResponse({
                    'success': True,
                    'data': extracted_data
                })
            except Exception as e:
                print(f"Extraction error: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Data extraction failed: {str(e)}'
                })

        except Exception as e:
            print(f"Processing error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Processing failed: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request or missing files'
    })


# views.py
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime

# views.py
# views.py
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def generate_pdf(request):
    if request.method == 'POST':
        try:
            # Get form data from request
            form_data = json.loads(request.body)
            
            # Prepare context with form data
            context = {
                'patient': {
                    'title': form_data.get('title', ''),
                    'first_name': form_data.get('first_name', ''),
                    'middle_name': form_data.get('middle_name', ''),
                    'last_name': form_data.get('last_name', ''),
                    'father_name': form_data.get('father_name', ''),
                    'date_of_birth': form_data.get('date_of_birth', ''),
                    'gender': form_data.get('gender', ''),
                    'marital_status': form_data.get('marital_status', ''),
                    'patient_id': form_data.get('patient_id', ''),
                    'street': form_data.get('street', ''),
                    'city': form_data.get('city', ''),
                    'country': form_data.get('country', '')
                },
                'emergency_contact': {
                    'name': form_data.get('emergency_name', ''),
                    'relationship': form_data.get('emergency_relationship', ''),
                    'phone': form_data.get('emergency_phone', ''),
                    'email': form_data.get('emergency_email', '')
                },
                'registration_date': datetime.now().strftime("%d/%m/%Y")
            }
            
            # Render template
            template = get_template('patient_pdf.html')
            html = template.render(context)
            
            # Create PDF
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
            
            if not pdf.err:
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="patient_details.pdf"'
                return response
            
            return HttpResponse('Error generating PDF', status=400)
            
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    
    return HttpResponse('Invalid request method', status=405)




from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import Doctor, Schedule, Appointment

def doctor_schedule_view(request):

    if not Doctor.objects.exists():
        Doctor.objects.create(name="Doctor A", department="General")
        Doctor.objects.create(name="Doctor B", department="General")

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            current_date = start_date
            while current_date <= end_date:
                Schedule.objects.create(
                    doctor=doctor,
                    date=current_date,
                    start_time=start_time,
                    end_time=end_time
                )
                current_date += timedelta(days=1)
                
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    doctors = Doctor.objects.all()
    return render(request, 'myapp\doctor_schedule.html', {'doctors': doctors})

def appointment_booking_view(request):
    if request.method == 'POST':
        patient_name = request.POST.get('patient_name')
        schedule_id = request.POST.get('schedule_id')
        
        try:
            schedule = Schedule.objects.get(id=schedule_id, is_available=True)
            
            Appointment.objects.create(
                patient_name=patient_name,
                doctor=schedule.doctor,
                schedule=schedule,
                status='CONFIRMED'
            )
            
            schedule.is_available = False
            schedule.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    doctors = Doctor.objects.all()
    return render(request, 'myapp/appointment_booking.html', {'doctors': doctors})

def get_schedule_events(request):
    """API endpoint to get schedule events for calendar"""
    try:
        doctor_id = request.GET.get('doctor')
        events = []
        
        schedules = Schedule.objects.all()
        if doctor_id:
            schedules = schedules.filter(doctor_id=doctor_id)

        for schedule in schedules:
            events.append({
                'title': f'Dr. {schedule.doctor.name} ({schedule.start_time}-{schedule.end_time})',
                'start': schedule.date.isoformat(),
                'className': 'available' if schedule.is_available else 'booked'
            })

        return JsonResponse({'events': events})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_available_slots(request, doctor_id, date):
    """API endpoint to get available slots"""
    try:
        available_slots = Schedule.objects.filter(
            doctor_id=doctor_id,
            date=date,
            is_available=True
        ).values('id', 'start_time', 'end_time')
        
        slots_list = list(available_slots)
        for slot in slots_list:
            slot['start_time'] = slot['start_time'].strftime('%H:%M')
            slot['end_time'] = slot['end_time'].strftime('%H:%M')

        return JsonResponse({
            'status': 'success',
            'slots': slots_list
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})