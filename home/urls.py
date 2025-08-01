from django.urls import path
from . import views

urlpatterns = [
    # Main/Home Page
    path('', views.index, name='index'),
    path('select-result-type/', views.select_result_type_view, name='select_result_type'),

    # School/College Result URLs
    path('create-school-result/', views.create_school_result, name='create_school_result'),
    path('show-school-results/', views.show_school_results, name='show_school_results'),
    path('export-school-pdf/<int:student_id>/', views.export_school_pdf, name='export_school_pdf'),
    path('export-school-excel/<int:student_id>/', views.export_school_excel, name='export_school_excel'),
    path('export-all-school-pdf/', views.export_all_school_pdf, name='export_all_school_pdf'),
    path('export-all-school-excel/', views.export_all_school_excel, name='export_all_school_excel'),
    path('clear-all-school-data/', views.clear_all_school_data, name='clear_all_school_data'),

    # University Result URLs
    path('create-university-result/', views.create_university_result, name='create_university_result'),
    path('show-university-results/', views.show_university_results, name='show_university_results'),
    path('export-university-pdf/<int:student_id>/', views.export_university_pdf, name='export_university_pdf'),
    path('export-university-excel/<int:student_id>/', views.export_university_excel, name='export_university_excel'),
    path('export-all-university-pdf/', views.export_all_university_pdf, name='export_all_university_pdf'),
    path('export-all-university-excel/', views.export_all_university_excel, name='export_all_university_excel'),
    path('clear-all-university-data/', views.clear_all_university_data, name='clear_all_university_data'),
]