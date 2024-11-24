from django.db import models
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404


class EmployeeQuerySet(models.query.QuerySet):

    def employee_age(self):
        return self.count()

    def employee_list(self):
        return self.only('name', 'emp_id', 'phone_no', 'company__company_name', 'designation__name')

    # def delete(self):
    #     return self.update(is_active=False)


class EmployeeManager(models.Manager):

    def get_queryset(self):
        return EmployeeQuerySet(self.model, self._db)

    def employee_age(self):
        return self.get_queryset().employee_age()

    def employee_list(self):
        return self.get_queryset().employee_list()

    # def delete(self):
    #     return self.get_queryset().delete()


