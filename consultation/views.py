from django.shortcuts import render
from django.http import HttpResponse
from .forms import ConsultationForm
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.utils import timezone
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os

def get_logo_path(clinic_logo_file):
    """
    Get the full URL path for the clinic logo.
    """
    if clinic_logo_file:
        file_name = clinic_logo_file.name
        return f"{settings.BASE_URL}:8000/media/clinic_logos/{file_name}"
    return ''

def extract_form_data(form):
    """
    Extract necessary data from the form.
    """
    return {
        'clinic_name': form.cleaned_data.get('clinic_name'),
        'physician_name': form.cleaned_data.get('physician_name'),
        'patient_last_name': form.cleaned_data.get('patient_last_name'),
        'patient_first_name': form.cleaned_data.get('patient_first_name'),
        'patient_dob': form.cleaned_data.get('patient_dob'),
        'consultation_note': form.cleaned_data.get('consultation_note'),
        'chief_complaint': form.cleaned_data.get('chief_complaint'),
        'clinic_logo_file': form.cleaned_data.get('clinic_logo'),
    }

def create_pdf_response(patient_last_name, patient_first_name, patient_dob):
    """
    Create an HTTP response for the PDF with the correct headers.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=CR_{patient_last_name}_{patient_first_name}_{patient_dob}.pdf'
    return response

def draw_logo(c, logo_path, width, height):
    """
    Draw the clinic logo on the PDF.
    """
    if logo_path:
        x_position = width - 2*inch - 50
        y_position = height - 100
        c.drawImage(logo_path, x_position, y_position, width=2*inch, height=0.5*inch)

def create_table(data):
    """
    Create a table with the given data.
    """
    table = Table(data, colWidths=[2*inch, 4*inch])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    return table

def draw_footer(c, request):
    """
    Draw the footer on the PDF.
    """
    footer_text = f"This report is generated on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} from {request.META.get('REMOTE_ADDR', 'Unknown IP')}"
    c.drawString(50, 30, footer_text)

def generate_pdf_view(request):
    if request.method == "POST":
        form = ConsultationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # Extract data from the form
            form_data = extract_form_data(form)
            logo_path = get_logo_path(form_data['clinic_logo_file'])

            # Create response and buffer for PDF
            response = create_pdf_response(form_data['patient_last_name'], form_data['patient_first_name'], form_data['patient_dob'])
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Draw logo
            draw_logo(c, logo_path, width, height)

            # Prepare table data
            data = [
                ['Clinic Name:', form_data['clinic_name']],
                ['Physician Name:', form_data['physician_name']],
                ['Patient Name:', f"{form_data['patient_first_name']} {form_data['patient_last_name']}"],
                ['Date of Birth:', form_data['patient_dob']],
                ['Chief Complaint:', form_data['chief_complaint']],
                ['Consultation Note:', form_data['consultation_note']]
            ]

            # Create and draw the table
            table = create_table(data)
            table.wrapOn(c, width, height)
            table.drawOn(c, 50, height - 300)

            # Draw footer
            draw_footer(c, request)

            # Finalize the PDF
            c.showPage()
            c.save()

            # Get PDF content and write to response
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            
            return response
        else:
            return render(request, 'consultation.html', {'form': form})

    return render(request, 'consultation.html')