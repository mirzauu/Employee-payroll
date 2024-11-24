from django.contrib import admin
from apps.general.models import Services, Designation, Banks


# Register your models here.

@admin.register(Services)
class ServiceAdmin(admin.ModelAdmin):

    search_fields = ['service_name']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):

    search_fields = ['designation']


admin.site.register(Banks)
# admin.site.register(Test)
