import django_filters
from django_filters import FilterSet, Filter
from apps.clients.models import Client
from rest_framework.filters import BaseFilterBackend


class ClientFilter(django_filters.FilterSet):

    client_name = django_filters.CharFilter(field_name='id', lookup_expr='icontains')
    sector = django_filters.CharFilter(field_name='sector', lookup_expr='icontains')

    class Meta:
        model = Client
        fields = ['client_name', 'sector']


class PayslipFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if 'client' in request.query_params:
            queryset = queryset.filter(emp__current_company__id=request.query_params['client'])
        if 'month' in request.query_params:
            queryset = queryset.filter(month=request.query_params['month'])
        if 'year' in request.query_params:
            queryset = queryset.filter(year=request.query_params['year'])
        return queryset

