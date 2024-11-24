from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('client-list/', views.ClientListView.as_view(), name='client-list'),
    path('client-filter-list/', views.ClientFilterView.as_view(), name='client-filtered-list'),
    path('client-detail/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('create-client/', views.ClientCreateView.as_view()),
    path('emp-shift/', views.EmployeeShiftView.as_view()),
    path('emp-shift-list/', views.ShiftEmployeeList.as_view()),
    path('emp_reassing/<int:pk>/', views.ShiftEmployeeDetails.as_view()),
    path('client-option-list/', views.ClientOptionView.as_view()),
    path('client-emp-list/<int:pk>/', views.ClientEmpListView.as_view()),
    path('rule-option/', views.RuleOptionView.as_view()),
    path('payroll-settings/', views.ClientSettingView.as_view()),
    path('payroll-setting-option/', views.ClientSettingOptionView.as_view()),
    path('details/payroll-settings/<int:pk>/', views.UpdateClientSettings.as_view()),
    path('generate-payslip/<int:pk>/', views.GeneratePayslip.as_view()),
    path('payslip-list/', views.GeneratedPayslipList.as_view()),
    path('payslip-details/<int:id>/', views.PayslipDetailsView.as_view()),
    path('salary-structure/<int:pk>/', views.ClientSalaryComponentView.as_view()),
    path('salary-structure-detail/<int:pk>/', views.SalaryComponentDetailView.as_view())
]
