from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import AccountManager
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model
# Create your models here.


def validate_name(value):
    if value and not value.isalpha():
        raise ValidationError("No Numbers are Allowed")
    return value


class Account(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("Email Field"), unique=True, max_length=30)
    username = models.CharField(_("username"), unique=True, max_length=20)
    first_name = models.CharField(_("first name"), max_length=20, validators=[validate_name])
    last_name = models.CharField(_("last_name"), max_length=20, validators=[validate_name])
    image = models.ImageField(blank=True, null=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting account."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = AccountManager()

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Account'

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name


class LoginHistory(models.Model):
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='login_histoty')
    ip = models.CharField(max_length=15, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    is_login = models.BooleanField(default=True, null=True, blank=True)
    is_logged_in = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.id} - {self.user} - {self.ip}"
    
    def __eq__(self, other: object) -> bool:
        return self.ip == other.ip and self.user_agent == other.user_agent
    
    def __hash__(self) -> int:
        return hash(('ip', self.ip, 'user_agent',self.user_agent))
    
    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'