from django.db import models
from django_extensions.db.models import TimeStampedModel
from apps.general.models import Services, Designation
from django.utils import timezone

# Create your models here.


class Client(TimeStampedModel):

    STATE_GOVT = 'state_govt'
    CENTRAL_GOVT = 'central_govt'
    PRIVATE = 'private'

    DAY_SHIFT = 'day_shift'
    NIGHT_SHIFT = 'night_shift'
    ROUND_SHIFT = 'round_shift'

    SQ_FEET = 'sq_feet'
    MAN_POWER = 'man_power'

    SECTOR_CHOICES = (
        (STATE_GOVT, 'State Govt'),
        (CENTRAL_GOVT, 'Central Govt'),
        (PRIVATE, 'Private'),
    )

    SHIFT_CHOICES = (
        (DAY_SHIFT, 'Day Shift'),
        (NIGHT_SHIFT, 'Night Shift'),
        (ROUND_SHIFT, 'Round Shift')
    )

    BILLING_CHOICES = (
        (SQ_FEET, 'Sq Feet'),
        (MAN_POWER, 'Man Power')
    )

    client_name = models.CharField(max_length=50)
    sector = models.CharField(choices=SECTOR_CHOICES, max_length=20)
    client_gst = models.CharField(max_length=255, blank=True, null=True)
    contract_singed = models.DateField(blank=True, null=True)
    contract_period = models.DateField(blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    client_phone = models.CharField(max_length=20, null=True, blank=True, unique=True)
    client_address = models.TextField()
    client_city = models.CharField(max_length=50, blank=True, null=True)
    client_pincode = models.CharField(max_length=50, blank=True, null=True)
    service = models.ManyToManyField(Services, blank=True, related_name='client_services')
    designation = models.ManyToManyField(Designation, blank=True, related_name='client_designations')
    lut_tenure = models.CharField(max_length=50, blank=True, null=True)
    billing_type = models.CharField(choices=BILLING_CHOICES, max_length=20)
    shift_type = models.CharField(choices=SHIFT_CHOICES, max_length=20)
    client_logo = models.ImageField(upload_to='client_logos', default='default_logo.jpg', blank=True, null=True)
    active_status = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Client'

    def __str__(self):
        return self.client_name

    @property
    def is_night(self):
        if self.shift_type == self.NIGHT_SHIFT:
            return True
        else:
            return False


class Rule(TimeStampedModel):

    rules = models.CharField(max_length=200)

    def __str__(self):
        return self.rules


class ClientSalarySettings(TimeStampedModel):
    MONTHLY = 'monthly'
    DAILY = 'daily'
    PERCENTAGE = 'percentage'
    VALUE = 'value'
    NOVALUE = False

    Salary_Choices = (
        ('Monthly', MONTHLY),
        ('Daily', DAILY)
    )

    Bonus_Choices = (
        ('None', NOVALUE),
        ('Percentage', PERCENTAGE),
        ('Value', VALUE)
    )

    company = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='salary_components')
    salary_type = models.CharField(max_length=50, choices=Salary_Choices, default=MONTHLY)
    epf_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    esi_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_choice = models.CharField(max_length=20, choices=Bonus_Choices, default=PERCENTAGE)
    bonus_value = models.CharField(max_length=20, default=0)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='client_rule')

    def __str__(self):
        return f"{self.company} - Settings"


class EarningsComponent(TimeStampedModel):

    client_settings = models.ForeignKey(ClientSalarySettings, on_delete=models.CASCADE, related_name='client_earnings')
    employee_type = models.ForeignKey(Designation, on_delete=models.CASCADE, related_name='client_salary_components')
    basic_vda = models.DecimalField(max_digits=10, decimal_places=2)
    earnings_components = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.client_settings.company} - {self.employee_type} Earning Components'

    @property
    def get_basic_vda(self):
        return self.basic_vda


class DeductionComponent(TimeStampedModel):

    earnings = models.ForeignKey(EarningsComponent, on_delete=models.CASCADE,
                                            related_name='deductions')
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2)
    lwf_amount = models.DecimalField(max_digits=10, decimal_places=2)
    canteen = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    swf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deduction_components = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.earnings.client_settings.company} - {self.earnings.employee_type} Deduction Components'
