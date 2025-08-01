from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Student, Subject, UniversityResult, UniversitySubject
from datetime import datetime

# ReportLab imports for PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# csv import for Excel/CSV
import csv

# Function to get the GPA from a given mark
def get_gpa_from_mark(mark):
    """
    Calculates GPA based on a simple 100-point scale.
    """
    if 80 <= mark <= 100:
        return 5.00
    elif 70 <= mark <= 79:
        return 4.00
    elif 60 <= mark <= 69:
        return 3.50
    elif 50 <= mark <= 59:
        return 3.00
    elif 40 <= mark <= 49:
        return 2.00
    else:
        return 0.00

# Function to get the letter grade from a given mark
def get_letter_grade(mark):
    """
    Assigns a letter grade based on a simple 100-point scale.
    """
    if 80 <= mark <= 100:
        return "A+"
    elif 70 <= mark <= 79:
        return "A"
    elif 60 <= mark <= 69:
        return "A-"
    elif 50 <= mark <= 59:
        return "B"
    elif 40 <= mark <= 49:
        return "C"
    else:
        return "F"

def index(request):
    """
    Renders the main home page.
    """
    return render(request, 'home/index.html')

def select_result_type_view(request):
    """
    Renders the page where the user selects between a school or university result sheet.
    """
    return render(request, 'home/select_result_type.html')

# ----------------------------------------------------------------------
# School/College Result Views
# ----------------------------------------------------------------------

def create_school_result(request):
    """
    Handles the creation of a result sheet for a school or college.
    This logic has been updated to NOT use credits.
    """
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        subjects_data = []

        subject_indices = sorted([int(key.split('_')[-1]) for key in request.POST if key.startswith('subject_name_')])

        for index in subject_indices:
            subject_name = request.POST.get(f'subject_name_{index}')
            mark_str = request.POST.get(f'mark_{index}')
            semester = request.POST.get(f'semester_{index}')
            try:
                mark = float(mark_str) if mark_str else 0.0
                if mark < 0 or mark > 100:
                    mark = 0.0

                subjects_data.append({
                    'name': subject_name,
                    'mark': mark,
                    'semester': semester
                })
            except (ValueError, TypeError):
                continue
        
        if not student_name or not subjects_data:
            return redirect('create_school_result')
        
        student = Student.objects.create(name=student_name)
        total_gpa = 0.0
        total_subjects = 0
        for sub in subjects_data:
            subject_gpa = get_gpa_from_mark(sub['mark'])
            letter_grade = get_letter_grade(sub['mark'])
            Subject.objects.create(
                student=student,
                name=sub['name'],
                mark=sub['mark'],
                credits=0,  # Setting credits to 0 since they are not used
                semester=sub['semester'],
                subject_gpa=subject_gpa,
                grade=letter_grade
            )
            total_gpa += subject_gpa
            total_subjects += 1
        
        if total_subjects > 0:
            student.cumulative_gpa = total_gpa / total_subjects
        else:
            student.cumulative_gpa = 0.0
        
        student.num_subjects = len(subjects_data)
        student.save()
        return redirect('show_school_results')

    return render(request, 'home/create_school_result.html')

def show_school_results(request):
    """
    Displays all school/college student results.
    """
    students = Student.objects.all().order_by('-entry_date')
    return render(request, 'home/show_school_results.html', {'students': students})

# ----------------------------------------------------------------------
# University Result Views (No Changes)
# ----------------------------------------------------------------------

def create_university_result(request):
    """
    Handles the creation of a result sheet for a university student.
    """
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        subjects_data = []

        subject_indices = sorted([int(key.split('_')[-1]) for key in request.POST if key.startswith('subject_name_')])

        for index in subject_indices:
            subject_name = request.POST.get(f'subject_name_{index}')
            mark_str = request.POST.get(f'mark_{index}')
            credits_str = request.POST.get(f'credits_{index}')
            semester = request.POST.get(f'semester_{index}')
            try:
                mark = float(mark_str) if mark_str else 0.0
                credits = int(credits_str) if credits_str else 0
                if mark < 0 or mark > 100:
                    mark = 0.0
                if credits < 0:
                    credits = 0
                subjects_data.append({
                    'name': subject_name,
                    'mark': mark,
                    'credits': credits,
                    'semester': semester
                })
            except (ValueError, TypeError):
                continue
        
        if not student_name or not subjects_data:
            return redirect('create_university_result')

        # Create new UniversityResult object
        student = UniversityResult.objects.create(name=student_name)
        total_gpa_points = 0
        total_credits = 0
        for sub in subjects_data:
            # Note: You might want a different GPA calculation for university
            subject_gpa = get_gpa_from_mark(sub['mark'])
            letter_grade = get_letter_grade(sub['mark'])
            UniversitySubject.objects.create(
                student=student,
                name=sub['name'],
                mark=sub['mark'],
                credits=sub['credits'],
                semester=sub['semester'],
                subject_gpa=subject_gpa,
                grade=letter_grade
            )
            if sub['credits'] > 0:
                total_gpa_points += subject_gpa * sub['credits']
                total_credits += sub['credits']
        
        if total_credits > 0:
            student.cumulative_gpa = total_gpa_points / total_credits
        else:
            student.cumulative_gpa = 0.0
        
        student.num_subjects = len(subjects_data)
        student.save()
        return redirect('show_university_results') # Redirect to the university results page

    return render(request, 'home/create_university_result.html')

def show_university_results(request):
    """
    Displays all university student results.
    """
    students = UniversityResult.objects.all().order_by('-entry_date')
    return render(request, 'home/show_university_results.html', {'students': students})

# ----------------------------------------------------------------------
# Export/Data Management Views (updated for school results)
# ----------------------------------------------------------------------

# New view function to export all school/college results as a single PDF file
def export_all_school_pdf(request):
    students = Student.objects.all().order_by('-entry_date')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_school_results.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    story.append(Paragraph("All School Results", styles['Title']))
    story.append(Spacer(1, 24))

    if not students:
        story.append(Paragraph("No school data available.", styles['Normal']))
    else:
        for student in students:
            story.append(Paragraph(f"<b>Student Name:</b> {student.name}", styles['Normal']))
            story.append(Paragraph(f"<b>Overall GPA:</b> {student.cumulative_gpa:.2f}", styles['Normal']))
            story.append(Paragraph(f"<b>Entry Date:</b> {student.entry_date.strftime('%B %d, %Y')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Updated to remove Credits
            data = [['Subject', 'Mark', 'Semester', 'Grade', 'Subject GPA']]
            for sub in student.subjects.all():
                data.append([sub.name, f"{sub.mark:.2f}", sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
            
            table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.skyblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
            
            # Adjusted colWidths for new column count
            pdf_table = Table(data, colWidths=[120, 50, 70, 50, 70])
            pdf_table.setStyle(table_style)
            story.append(pdf_table)
            story.append(Spacer(1, 36))
    doc.build(story)
    return response

# New view function to export all school/college results as a single CSV file
def export_all_school_excel(request):
    students = Student.objects.all().order_by('-entry_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_school_results.csv"'
    writer = csv.writer(response)
    
    # Updated to remove Credits
    writer.writerow(['Student Name', 'Overall GPA', 'Entry Date', 'Subject', 'Mark', 'Semester', 'Grade', 'Subject GPA'])
    
    if not students:
        writer.writerow(['No school data available.'])
        return response
    for student in students:
        for sub in student.subjects.all():
            # Updated to remove Credits
            writer.writerow([student.name, f"{student.cumulative_gpa:.2f}", student.entry_date.strftime('%Y-%m-%d'), sub.name, f"{sub.mark:.2f}", sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
    return response

# New view function to clear all school/college data
def clear_all_school_data(request):
    if request.method == 'POST':
        Student.objects.all().delete()
        Subject.objects.all().delete()
        return redirect('show_school_results')
    return redirect('show_school_results')

# New view function to export all university results as a single PDF file
def export_all_university_pdf(request):
    students = UniversityResult.objects.all().order_by('-entry_date')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_university_results.pdf"'
    # (Rest of the PDF generation logic for university results)
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("All University Results", styles['Title']))
    story.append(Spacer(1, 24))
    if not students:
        story.append(Paragraph("No university data available.", styles['Normal']))
    else:
        for student in students:
            story.append(Paragraph(f"<b>Student Name:</b> {student.name}", styles['Normal']))
            story.append(Paragraph(f"<b>Overall GPA:</b> {student.cumulative_gpa:.2f}", styles['Normal']))
            story.append(Paragraph(f"<b>Entry Date:</b> {student.entry_date.strftime('%B %d, %Y')}", styles['Normal']))
            story.append(Spacer(1, 12))
            data = [['Subject', 'Mark', 'Credits', 'Semester', 'Grade', 'Subject GPA']]
            for sub in student.subjects.all():
                data.append([sub.name, f"{sub.mark:.2f}", str(sub.credits), sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
            table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.skyblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
            pdf_table = Table(data, colWidths=[120, 50, 50, 70, 50, 70])
            pdf_table.setStyle(table_style)
            story.append(pdf_table)
            story.append(Spacer(1, 36))
    doc.build(story)
    return response

# New view function to export all university results as a single CSV file
def export_all_university_excel(request):
    students = UniversityResult.objects.all().order_by('-entry_date')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_university_results.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student Name', 'Overall GPA', 'Entry Date', 'Subject', 'Mark', 'Credits', 'Semester', 'Grade', 'Subject GPA'])
    if not students:
        writer.writerow(['No university data available.'])
        return response
    for student in students:
        for sub in student.subjects.all():
            writer.writerow([student.name, f"{student.cumulative_gpa:.2f}", student.entry_date.strftime('%Y-%m-%d'), sub.name, f"{sub.mark:.2f}", str(sub.credits), sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
    return response

# New view function to clear all university data
def clear_all_university_data(request):
    if request.method == 'POST':
        UniversityResult.objects.all().delete()
        UniversitySubject.objects.all().delete()
        return redirect('show_university_results')
    return redirect('show_university_results')

# New view function to export single school result as a PDF
def export_school_pdf(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    subjects = student.subjects.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="result_{student.name}_{student.entry_date.strftime("%Y-%m-%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph(f"Student Result Sheet", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Student Name: <b>{student.name}</b>", styles['Normal']))
    story.append(Paragraph(f"Overall GPA: <b>{student.cumulative_gpa:.2f}</b>", styles['Normal']))
    story.append(Paragraph(f"Date: {student.entry_date.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Updated to remove Credits
    data = [['Subject', 'Mark', 'Semester', 'Grade', 'Subject GPA']]
    for sub in subjects:
        data.append([sub.name, f"{sub.mark:.2f}", sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
    
    table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.skyblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    
    # Adjusted colWidths for new column count
    pdf_table = Table(data, colWidths=[120, 50, 70, 50, 70])
    pdf_table.setStyle(table_style)
    story.append(pdf_table)
    doc.build(story)
    return response

# New view function to export single school result as an Excel/CSV file
def export_school_excel(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    subjects = student.subjects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="result_{student.name}_{student.entry_date.strftime("%Y-%m-%d")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student Name', student.name])
    writer.writerow(['Overall GPA', f"{student.cumulative_gpa:.2f}"])
    writer.writerow(['Entry Date', student.entry_date.strftime('%Y-%m-%d')])
    writer.writerow([])
    
    # Updated to remove Credits
    writer.writerow(['Subject', 'Mark', 'Semester', 'Grade', 'Subject GPA'])
    for sub in subjects:
        # Updated to remove Credits
        writer.writerow([sub.name, sub.mark, sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
    return response

# New view function to export single university result as a PDF
def export_university_pdf(request, student_id):
    student = get_object_or_404(UniversityResult, pk=student_id)
    subjects = student.subjects.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="university_result_{student.name}_{student.entry_date.strftime("%Y-%m-%d")}.pdf"'
    # (PDF generation logic)
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph(f"University Result Sheet", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Student Name: <b>{student.name}</b>", styles['Normal']))
    story.append(Paragraph(f"Overall GPA: <b>{student.cumulative_gpa:.2f}</b>", styles['Normal']))
    story.append(Paragraph(f"Date: {student.entry_date.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 24))
    data = [['Subject', 'Mark', 'Credits', 'Semester', 'Grade', 'Subject GPA']]
    for sub in subjects:
        data.append([sub.name, f"{sub.mark:.2f}", str(sub.credits), sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
    table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.skyblue), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.white), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    pdf_table = Table(data, colWidths=[120, 50, 50, 70, 50, 70])
    pdf_table.setStyle(table_style)
    story.append(pdf_table)
    doc.build(story)
    return response

# New view function to export single university result as an Excel/CSV file
def export_university_excel(request, student_id):
    student = get_object_or_404(UniversityResult, pk=student_id)
    subjects = student.subjects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="university_result_{student.name}_{student.entry_date.strftime("%Y-%m-%d")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student Name', student.name])
    writer.writerow(['Overall GPA', f"{student.cumulative_gpa:.2f}"])
    writer.writerow(['Entry Date', student.entry_date.strftime('%Y-%m-%d')])
    writer.writerow([])
    writer.writerow(['Subject', 'Mark', 'Credits', 'Semester', 'Grade', 'Subject GPA'])
    for sub in subjects:
        writer.writerow([sub.name, sub.mark, sub.credits, sub.semester, sub.grade, f"{sub.subject_gpa:.2f}"])
    return response