from django.urls import path
from . import views

app_name = "employees"

urlpatterns = [
    path('emp/', views.EmployeeView.as_view(), name="employee"),
    path('emp/<str:emp_id>/', views.EmployeeDetailsView.as_view(), name="employee-details"),
    path('emp-bank-create/', views.EmployeeBankCreateView.as_view()),
    path('emp-bank-details/<str:pk>/', views.EmployeeBankDetailView.as_view()),
    path('loan-list/', views.LoanView.as_view()),
    path('emp-loan-list/', views.EmployeeLoanView.as_view()),
    path('create-emploan/', views.CreateEmployeeLoad.as_view()),
    path('loan/<int:pk>/', views.LoanDetailView.as_view()),
    path('attendance/<int:pk>/', views.AttendanceView.as_view()),
    path('attendance-not-generated/<int:pk>/', views.AttendanceNotGeneratedView.as_view()),
    path('attendance-details/<int:pk>/', views.AttendanceDetailView.as_view()),
    path('emp-payslip-list/<str:emp_id>/', views.PayslipView.as_view()),
    path('emp-paystructure/<int:id>/', views.EmployeePayStructureView.as_view()),

    path('upload-employees/', views.bulk_upload_employees, name='upload_employees'),
]
