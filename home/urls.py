# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-result-sheet/', views.create_result_sheet_view, name='create_result_sheet'),
    path('results/', views.show_result, name='show_result'),
    path('export-pdf/<int:student_id>/', views.export_pdf, name='export_pdf'),
    path('export-excel/<int:student_id>/', views.export_excel, name='export_excel'),
    path('clear-all/', views.clear_all_data, name='clear_all_data'),
    
    # New URLs for exporting all data
    path('export-all-pdf/', views.export_all_pdf, name='export_all_pdf'),
    path('export-all-excel/', views.export_all_excel, name='export_all_excel'),
]