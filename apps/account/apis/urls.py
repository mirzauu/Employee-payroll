from django.urls import path
from .views import RegisterUserView, LoginView, LogoutView

app_name = 'account'

urlpatterns = [
    path('register-user/', RegisterUserView.as_view(), name='register_user'),
    path('login/', LoginView.as_view(), name='login-user'),
    path('logout/', LogoutView.as_view(), name='logout-user')

]
