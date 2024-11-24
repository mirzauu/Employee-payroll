from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin
from .forms import SingUpForm
from .models import LoginHistory
# Register your models here.


class AccountAdmin(UserAdmin):
    model = Account
    add_form = SingUpForm
    search_fields = ('email',)
    list_filter = ('email', 'username', 'is_staff')
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    # ordering = ('-data_joined',)


class LoginHistoryAdmin(admin.ModelAdmin):
        list_display = ['user', 'id', 'date_time', 'ip', 'user_agent', 'is_logged_in', 'get_action_status']
        list_filter = ['user']

        def get_action_status(self, obj):
              if obj.is_login:
                    return "Login"
              return "Logout"
        
        def has_add_permission(self, request):
            return False
        
        get_action_status.short_description = "Status"


admin.site.register(Account, AccountAdmin)
admin.site.register(LoginHistory, LoginHistoryAdmin)
