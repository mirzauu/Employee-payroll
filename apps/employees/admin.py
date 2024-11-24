from django.contrib import admin
from apps.employees.models import (Employee, EmployeeBank, EmployeeHistory, ShiftEmployee, EmployeeAttendance,
                                   EmployeeLoan, LoanHistory, Payslip, DeletedEmployee)

# Register your models here.


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_company', 'designation', 'uanNumber')
    list_editable = ('current_company', 'designation')
    list_filter = ('designation', 'current_company', 'uanNumber')


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeBank)
admin.site.register(EmployeeHistory)
admin.site.register(ShiftEmployee)
admin.site.register(EmployeeAttendance)
admin.site.register(EmployeeLoan)
admin.site.register(LoanHistory)
admin.site.register(Payslip)
admin.site.register(DeletedEmployee)
