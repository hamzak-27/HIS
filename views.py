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
            # Create a modified POST data dictionary
            emergency_data = {
                'name': request.POST.get('emergency-name'),
                'relationship': request.POST.get('emergency-relationship'),
                'phone': request.POST.get('emergency-phone'),
                'email': request.POST.get('emergency-email')
            }
            
            family_data = {
                'name': request.POST.get('family-name'),
                'relationship': request.POST.get('family-relationship'),
                'contact': request.POST.get('family-contact')
            }
            
            guarantor_data = {
                'name': request.POST.get('guarantor-name'),
                'relationship': request.POST.get('guarantor-relationship'),
                'contact': request.POST.get('guarantor-contact'),
                'address': request.POST.get('guarantor-address')
            }

            patient_form = PatientRegistrationForm(request.POST)
            emergency_form = EmergencyContactForm(emergency_data)
            family_form = FamilyMemberForm(family_data)
            guarantor_form = GuarantorForm(guarantor_data)

            if all([
                patient_form.is_valid(),
                emergency_form.is_valid(),
                family_form.is_valid(),
                guarantor_form.is_valid()
            ]):
                patient = patient_form.save()
                
                emergency_contact = emergency_form.save(commit=False)
                emergency_contact.patient = patient
                emergency_contact.save()
                
                family_member = family_form.save(commit=False)
                family_member.patient = patient
                family_member.save()
                
                guarantor = guarantor_form.save(commit=False)
                guarantor.patient = patient
                guarantor.save()
                
                messages.success(request, 'Patient registered successfully!')
                return redirect('patient_list')
            else:
                print("Patient Form Errors:", patient_form.errors)
                print("Emergency Form Errors:", emergency_form.errors)
                print("Family Form Errors:", family_form.errors)
                print("Guarantor Form Errors:", guarantor_form.errors)
                messages.error(request, 'Please correct the errors in the form.')
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            messages.error(request, f'An error occurred: {str(e)}')
    else:
        patient_form = PatientRegistrationForm()
        emergency_form = EmergencyContactForm()
        family_form = FamilyMemberForm()
        guarantor_form = GuarantorForm()

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
def generate_patient_pdf(request, patient_id):
    try:
        # Get patient by patient_id (not database id)
        patient = Patient.objects.get(patient_id=patient_id)  # Using patient_id field
        emergency_contact = patient.emergency_contacts.first()
        
        # Prepare template context
        context = {
            'patient': patient,
            'emergency_contact': emergency_contact,
            'registration_date': datetime.now().strftime("%d/%m/%Y")
        }
        
        # Render template
        template = get_template('patient_pdf.html')
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        # Return PDF response
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"patient_{patient_id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        return HttpResponse('Error generating PDF', status=400)
    except Patient.DoesNotExist:
        return HttpResponse('Patient not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)