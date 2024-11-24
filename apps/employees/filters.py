import django_filters
from django_filters import FilterSet, Filter
from apps.employees.models import Employee
from rest_framework.filters import BaseFilterBackend


class EmployeeFilter(django_filters.FilterSet):

    emp_id = django_filters.CharFilter(field_name='emp_id', lookup_expr='iexact')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    company = django_filters.CharFilter(field_name='current_company__id', lookup_expr='icontains')
    phone_no = django_filters.CharFilter(field_name='phone_no', lookup_expr='iexact')

    class Meta:
        model = Employee
        fields = ['emp_id', 'current_company', 'name', 'phone_no']


class EmployeeLoanFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if 'emp_id' in request.query_params:
            queryset = queryset.filter(employee__emp_id=request.query_params['emp_id'])
        return queryset

