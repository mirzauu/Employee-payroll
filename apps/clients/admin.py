from django.contrib import admin
from apps.clients.models import Client, EarningsComponent, DeductionComponent, ClientSalarySettings, \
    Rule

# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    search_fields = ['service', 'designation']
    autocomplete_fields = ['service', 'designation']


admin.site.register(Rule)
admin.site.register(ClientSalarySettings)
admin.site.register(EarningsComponent)
admin.site.register(DeductionComponent)

