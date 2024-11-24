import json
from django.shortcuts import get_object_or_404
from rest_framework.views import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from apps.clients.models import Client
from apps.employees.models import Employee, Payslip, EmployeeLoan, LoanHistory
from apps.employees.apis.serializers import EmployeeSerializer, EmployeeCompanyListSerializer, PayslipSerializer, \
                PayslipListSerializer
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from apps.clients.filters import ClientFilter, PayslipFilter
from apps.clients.apis.serializers import ShiftEmpSerializer, EmployeeCompanyEdit, clientOptionSerializer, \
                        ClientSerializer, ClientListSerializer, ShiftEmployee, ShiftEmpListSerializer, RuleSerializer, \
                        ClientSalarySerializer, ClientSalaryOptionSerializer, SalaryComponentSerializer, \
                        SalaryStructureSerializer
from apps.clients.mixins import OptionMixin
from rest_framework import status
from apps.general.models import Services, Designation
from rest_framework.parsers import MultiPartParser, JSONParser
from apps.clients.models import ClientSalarySettings, EarningsComponent, DeductionComponent, Rule
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.rules.rules import BaseRule, DPRule
from django.http import JsonResponse
from django.forms.models import model_to_dict


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        page_count = response.data.get('count') // self.page_size + (1 if response.data.get('count') % self.page_size >
                                                                     0 else 0)
        return Response(OrderedDict([
            ('count', response.data.get('count')),
            ('next', response.data.get('next')),
            ('previous', response.data.get('previous')),
            ('page_count', page_count),
            ('success', True),
            ('data', data)
        ]))


class ClientFilterView(OptionMixin, generics.GenericAPIView):

    serializer_class = clientOptionSerializer

    def get_queryset(self):
        sector = self.request.GET.get('sector', None)
        queryset = Client.objects.filter(sector=sector)
        return queryset


class ClientListView(generics.ListAPIView):

    permission_classes = [IsAdminUser]
    queryset = Client.objects.only('client_name', 'sector', 'client_phone').all()
    serializer_class = ClientListSerializer
    pagination_class = CustomPagination
    filter_class = ClientFilter

    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        filter_set = self.filter_class(request.GET, self.get_queryset())
        if filter_set.is_valid():
            data = filter_set.qs
        paginated_data = self.paginate_queryset(data)
        serializer = self.get_serializer(paginated_data, many=True)
        try:
            if serializer:
                return self.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"success": False, "data": str(e)})
        

class ClientCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        data = {
            "client_name": request.data.get('client_name'),
            "sector": request.data.get('sector'),
            "client_gst": request.data.get('client_gst', None),
            "contract_singed": request.data.get('contract_singed'),
            "contract_period": request.data.get('contract_period'),
            "client_email": request.data.get('client_email'),
            "client_phone": request.data.get('client_phone'),
            "client_address": request.data.get('client_address'),
            "client_city": request.data.get('client_city'),
            "client_pincode": request.data.get('client_pincode', None),
            "service": json.loads(request.data.get('service')),
            "designation": json.loads(request.data.get('designation')),
            "lut_tenure": request.data.get('lut_tenure'),
            "billing_type": request.data.get('billing_type'),
            "shift_type": request.data.get('shift_type'),
            "client_logo": request.data.get('client_logo', None)
        }
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            print("Test Data", serializer.validated_data)
            serializer.save()
            return Response({"success": "New Client Added"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'pk'

    def get_serializer_context(self):
        serializer_context = {
            "hide_relationship": self.request.GET.get('hide_relationship', False),
            "request": self.request
        }
        return serializer_context

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(instance)
            serializer = self.get_serializer(instance)
            return Response({"success": True, "data": serializer.data})
        except Exception as e:
            return Response({"success": False, "data": str(e)})

    def put(self, request, *args, **kwargs):
        data = {
            "client_name": request.data.get('client_name'),
            "sector": request.data.get('sector'),
            "client_gst": request.data.get('client_gst'),
            "contract_singed": request.data.get('contract_singed'),
            "contract_period": request.data.get('contract_period'),
            "client_email": request.data.get('client_email'),
            "client_phone": request.data.get('client_phone'),
            "client_address": request.data.get('client_address'),
            "client_city": request.data.get('client_city'),
            "client_pincode": request.data.get('client_pincode'),
            "service": json.loads(request.data.get('service')),
            "designation": json.loads(request.data.get('designation')),
            "lut_tenure": request.data.get('lut_tenure'),
            "shift_type": request.data.get('shift_type'),
            "billing_type": request.data.get('billing_type'),
        }
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid()
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        except Exception as e:
            return Response({"success": False, "data": str(e)})

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EmployeeShiftView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ShiftEmpSerializer

    def post(self, request, *args, **kwargs):
        shift_type = request.data.get('shift_type')
        if shift_type == 'Temporary':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"success": True, "data": serializer.data})
        elif shift_type == 'Permenent':
            serializer = EmployeeCompanyEdit(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"success": True, "data": "Employee Shifted Successfull"})
        return Response({'success': False, "data": "Invalid Shift Type"})


class ShiftEmployeeList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = ShiftEmployee.objects.filter(is_active=True)
    serializer_class = ShiftEmpListSerializer
    pagination_class = CustomPagination


class ShiftEmployeeDetails(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = get_object_or_404(ShiftEmployee, id=kwargs.get('pk'))
        emp_instance = get_object_or_404(Employee, emp_id=queryset.emp_id.emp_id)
        
        emp_instance.current_company = queryset.prev_company
        emp_instance.save()

        queryset.is_active = False
        queryset.save_temporary()

        return Response({"success": True, "data": "Employee Shift Status Disabled"})


class ClientOptionView(OptionMixin, generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    queryset = Client.objects.all()
    serializer_class = clientOptionSerializer


class ClientEmpListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]

    queryset = Employee.objects.filter(is_active=True)
    serializer_class = EmployeeCompanyListSerializer
    pagination_class = CustomPagination
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = Employee.objects.filter(is_active=True, current_company=self.kwargs.get('pk'))
        return queryset


class GeneratePayslip(APIView):

    _rule_mapping = {
        DPRule: "GENERAL RULE",
        BaseRule: 'GENERAL RULE'
    }

    _data = dict()

    @staticmethod
    def query_to_dict(data, exclude=None):
        _result = model_to_dict(data, exclude=exclude)
        return _result

    def post(self, request, *args, **kwargs):
        employee = Employee.objects.get(emp_id=request.data['employee'])
        earnings = EarningsComponent.objects.get(client_settings__company=self.kwargs.get('pk'),
                                                 employee_type=employee.designation)
        deductions = DeductionComponent.objects.get(earnings=earnings)
        employee_loan = EmployeeLoan.objects.filter(employee=employee).first()
        rule = earnings.client_settings.rule.rules
        earn = self.query_to_dict(earnings, exclude=('id', 'client_settings', 'employee_type'))
        deduct = self.query_to_dict(deductions, exclude=('id', 'earnings'))
        if request.data.get('load_deduction', None):
            deduct['loan'] = employee_loan.deduction_amount if employee_loan else 0
        match rule:
            case "GENERAL RULE":
                _amount = BaseRule(earn, deduct, attendance=request.data['attendance'],
                                   bonus_type=earnings.client_settings.bonus_choice,
                                   bonus_value=earnings.client_settings.bonus_choice)
            case "DP WORLD RULE":
                _amount = DPRule(earn, deduct, attendance=request.data['attendance'])
            case "TECHNOPARK RULE":
                _amount = 'pass'
            case _:
                _amount = BaseRule(earn, attendance=20)

        self._data = {
            'employee_id': employee.emp_id,
            'employee_name': employee.name,
            'employee_company': employee.current_company.client_name,
            'employee_phone': employee.phone_no,
            'employee_designation': employee.designation.name,
            'month': request.data['month'],
            'year': request.data['year'],
            'attendance': request.data['attendance'],
            'earnings': _amount(),
            'deductions': _amount.get_deduction_components(),
            'total_earnings': _amount.get_earning_total(),
            'total_deductions': _amount.get_total_deductions(),
            'grand_total': round(_amount.get_earning_total() - _amount.get_total_deductions())
        }
        obj, created = Payslip.objects.update_or_create(
            emp=employee,
            year=request.data['year'],
            month=request.data['month'],
            defaults={
                'attendance': self._data['attendance'],
                'earnings': self._data['earnings'],
                'deductions': self._data['deductions'],
                'total_earnings': _amount.get_earning_total(),
                'total_deductions': _amount.get_total_deductions(),
                'grand_total': self._data['grand_total']
            }
        )
        if employee_loan and self.request.data.get('load_deduction', True):
            employee_loan.save_deduction()
            loan_history = LoanHistory()
            loan_history.save_loan_history(employee_loan)
        return Response({"success": self._data}, status=status.HTTP_200_OK)


class GeneratedPayslipList(generics.ListAPIView):

    serializer_class = PayslipListSerializer
    queryset = Payslip.objects.all()
    pagination_class = CustomPagination
    filter_backends = [PayslipFilter]


class PayslipDetailsView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PayslipSerializer
    queryset = Payslip.objects.all()
    lookup_field = 'id'
    
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class RuleOptionView(OptionMixin, generics.GenericAPIView):
    # permission_classes = [IsAdminUser]

    queryset = Rule.objects.all()
    serializer_class = RuleSerializer


class ClientSettingView(generics.ListCreateAPIView):

    queryset = ClientSalarySettings.objects.all()
    serializer_class = ClientSalarySerializer
    pagination_class = CustomPagination

    def get_serializer_context(self):
        return {
            "settings": False
        }


class UpdateClientSettings(generics.RetrieveUpdateDestroyAPIView):

    queryset = ClientSalarySettings.objects.all()
    serializer_class = ClientSalarySerializer
    lookup_field = 'pk'

    def get_serializer_context(self):
        return {
            "settings": True
        }


class ClientSettingOptionView(OptionMixin, generics.GenericAPIView):

    queryset = ClientSalarySettings.objects.all()
    serializer_class = ClientSalaryOptionSerializer


class ClientSalaryComponentView(generics.GenericAPIView):

    serializer_class = SalaryStructureSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = EarningsComponent.objects.filter(client_settings__company__id=self.kwargs.get('pk'))
        page = self.paginate_queryset(queryset)
        serializer = SalaryComponentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.validated_data)
            return Response({'success': "Data Created"})
        return Response({'error': serializer.errors})


class SalaryComponentDetailView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = 'pk'
    serializer_class = SalaryStructureSerializer

    def get_object(self):
        queryset = get_object_or_404(EarningsComponent, pk=self.kwargs.get('pk'))
        return queryset
