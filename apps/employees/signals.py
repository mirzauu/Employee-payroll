from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.db.models.signals import Signal
from apps.employees.models import Employee, DeletedEmployee
from django.forms.models import model_to_dict


employee_delete = Signal()


@receiver(employee_delete)
def delete_employee(sender, user, request, **kwargs):
    try:
        employee = Employee.objects.get(emp_id=user)
        emp_instance = model_to_dict(employee)
        DeletedEmployee.objects.create(employee_details=emp_instance)
    except Exception as e:
        print(str(e))

