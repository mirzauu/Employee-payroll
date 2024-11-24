import PIL.Image
from rest_framework.views import Response
from rest_framework import generics
from rest_framework.views import APIView
from ..models import Employee, EmployeeBank, EmployeeLoan, EmployeeAttendance, Payslip
from .serializers import EmployeeSerializer, EmployeeListSerializer, EmployeeBankSerializer, EmployeeLoanSerializer, \
                    EmployeeLoanDetailSerializer, AttendanceSerializer, PayslipSerializer, PayslipListSerializer, \
                    AttendanceListSerializer, EmployeeLoanListSerializer
from apps.clients.models import EarningsComponent, DeductionComponent
from apps.clients.apis.serializers import SalaryStructureSerializer
from rest_framework.parsers import FileUploadParser, MultiPartParser
from PIL import Image as PILImage
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.clients.apis.views import CustomPagination
from apps.employees.filters import EmployeeFilter, EmployeeLoanFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.employees.decorators import instance_check
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from django.db.models import Q
from apps.employees.signals import employee_delete


import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from apps.general.models import Designation 
from apps.clients.models import  Client
from ..forms import EmployeeUploadForm
from datetime import datetime


class EmployeeView(generics.ListCreateAPIView):

    # permission_classes = [IsAdminUser]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    pagination_class = CustomPagination
    filter_class = EmployeeFilter
    # parser_classes = [MultiPartParser]

    def get_queryset(self):
        queryset = Employee.objects.filter(is_active=True).only("name", "designation__name", "emp_id", "phone_no",
                                                                "current_company__client_name").all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_set = self.filter_class(request.GET, self.get_queryset())
        if filter_set.is_valid():
            queryset = filter_set.qs
        page = self.paginate_queryset(queryset)
        serializer = EmployeeListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.validated_data)
            return Response({"success": "New Employee Added"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.error}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'emp_id'

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        if not queryset:
            return Response({'success': False, 'message': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    
    # def put(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.update(serializer, serializer.validated_data)
    #     return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        employee_delete.send(sender=Employee, user=self.kwargs.get('emp_id'), request=request)
        return super().delete(request, *args, **kwargs)


class EmployeeBankCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = EmployeeBankSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response:
            return Response({"success": True, "data": response.data})
        return Response({"success": False, "error": "Invalid Data"})


class EmployeeBankDetailView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    queryset = EmployeeBank.objects.all()
    serializer_class = EmployeeBankSerializer

    def get_object(self):
        queryset = EmployeeBank.objects.get(employee__emp_id=self.kwargs.get('pk'))
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.get_serializer(queryset)
        return Response({"success": True, "data": serializer.data})

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'success': True, "data": serializer.data})
        return Response({'success': False, "error": serializer.errors})


class LoanView(generics.ListAPIView):

    queryset = EmployeeLoan.objects.all()
    serializer_class = EmployeeLoanListSerializer
    pagination_class = CustomPagination


class EmployeeLoanView(generics.ListAPIView):
    queryset = EmployeeLoan.objects.all()
    serializer_class = EmployeeLoanListSerializer
    pagination_class = CustomPagination
    filter_backends = [EmployeeLoanFilter]


class CreateEmployeeLoad(generics.CreateAPIView):

    queryset = Employee.objects.all()
    serializer_class = EmployeeLoanSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response:
            return Response({'success': True, "data": response.data})
        return Response({"success": False, "data": response.errors})


class LoanDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = EmployeeLoanDetailSerializer

    def get_object(self):
        queryset = get_object_or_404(EmployeeLoan, id=self.kwargs.get('pk'))
        return queryset

    def get(self, request, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response({"success": True, "data": serializer.data})


class AttendanceView(generics.GenericAPIView):

    serializer_class = AttendanceSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = EmployeeAttendance.objects.filter(is_active=True).filter(employee__current_company=self.kwargs.get('pk'),
                                                     year=request.GET.get('year'),
                                                     month=request.GET.get('month'))
        page = self.paginate_queryset(queryset)
        serializer = AttendanceListSerializer(page, many=True, context={'request': request})
        data = self.get_paginated_response(serializer.data)
        return data

    @instance_check('employee', 'month', 'year', kls=EmployeeAttendance)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success": True, "data": "Attendance Added"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AttendanceNotGeneratedView(generics.ListCreateAPIView):

    serializer_class = EmployeeListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Employee.objects.filter(current_company_id=self.kwargs.get('pk')).exclude(
                                            Q(employee_attendance__month=self.request.GET.get('month')) &
                                            Q(employee_attendance__year=self.request.GET.get('year'))
                                        )
        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = AttendanceSerializer
    queryset = EmployeeAttendance.objects.all()
    lookup_field = 'pk'


class PayslipView(generics.ListAPIView):

    lookup_field = 'emp_id'
    serializer_class = PayslipListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Payslip.objects.filter(emp__emp_id=self.kwargs.get('emp_id'))
        return queryset


class EmployeePayStructureView(generics.GenericAPIView):

    serializer_class = SalaryStructureSerializer

    def get_object(self):
        employee = Employee.objects.get(emp_id=2267)
        queryset = get_object_or_404(EarningsComponent,
                                     client_settings__company__client_name=employee.current_company.client_name,
                                     employee_type__name=employee.designation.name)
        return queryset

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object())
        return Response({'success': serializer.data})



def bulk_upload_employees(request):
    if request.method == "POST":
        form = EmployeeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Load the Excel file
                df = pd.read_excel(file)

                # Validate required columns
                required_columns = [
                    'emp_id', 'name', 'phone_no', 'gender', 'joining_date'
                ]
                for column in required_columns:
                    if column not in df.columns:
                        return HttpResponse(f"Missing column: {column}")

                # Validate and fetch details
                employee_details = []
                for _, row in df.iterrows():
                    try:
                        emp_id = row['emp_id']
                        name = row['name']
                        phone_no = row['phone_no']
                        gender = row['gender']

                        # Parse and format the joining_date
                        raw_joining_date = row['joining_date']
                        if isinstance(raw_joining_date, str):
                            joining_date = datetime.strptime(raw_joining_date.split(" ")[0], "%Y-%m-%d").date()
                        elif isinstance(raw_joining_date, pd.Timestamp):
                            joining_date = raw_joining_date.date()
                        else:
                            joining_date = raw_joining_date

                        # Fetch Designation object
                     
                        # Append details to the list
                        employee_details.append({
                            'emp_id': emp_id,
                            'name': name,
                            'phone_no': phone_no,
                            'gender': gender,
                            'joining_date': joining_date,
                            
                        })

                    except Exception as e:
                        return HttpResponse(f"Error in row {row}: {e}")

                # Render details to a template
                print(employee_details)
                return render(request, 'employee_details.html', {'employee_details': employee_details})

            except Exception as e:
                return HttpResponse(f"Error processing file: {e}")
    else:
        form = EmployeeUploadForm()
    return render(request, 'upload_employees.html', {'form': form})

