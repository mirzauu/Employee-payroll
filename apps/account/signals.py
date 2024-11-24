from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from . models import LoginHistory
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.db.models.signals import Signal


user_token_login = Signal()
user_token_logout = Signal()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    LoginHistory.objects.create(
        user=user,
        ip=ip,
        user_agent=request.META.get('HTTP_USER_AGENT'),
        is_login=True
    )


@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    if user:
        ip = get_client_ip(request)
        LoginHistory.objects.create(
            user=user,
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            is_login=False
        )


@receiver(user_token_login)
def token_login(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    LoginHistory.objects.create(
        user=user,
        ip=ip,
        user_agent=request.META.get('HTTP_USER_AGENT'),
        is_login=True
    )


@receiver(user_token_logout)
def token_logout(sender, user, request, **kwargs):
    if user:
        ip = get_client_ip(request)
        LoginHistory.objects.create(
            user=user,
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            is_login=False
        )
