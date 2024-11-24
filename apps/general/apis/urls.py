from django.urls import path
from . import views

app_name = "general"

urlpatterns = [
    path('service-list/', views.ServiceListView.as_view()),
    path('service-detail/<int:id>/', views.ServiceUpdateView.as_view()),
    path('service-option-list/', views.ServiceOptionView.as_view()),
    path('designation-list/', views.DesignationView.as_view()),
    path('designation-detail/<int:id>/', views.DesignationDetailView.as_view()),
    path('bank-option-list/', views.BankOptionView.as_view()),
    path('designation-option-list/', views.DesignationOptionView.as_view()),
    path('client-designation/<int:id>/', views.ClientDesignation.as_view()),
    path('banks/', views.BankView.as_view()),
    path('download-template/', views.UploadFileView.as_view()),
    path('demo/', views.DemoView.as_view())
]