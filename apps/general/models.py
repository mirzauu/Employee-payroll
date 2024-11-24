from django.db import models
from django_extensions.db.models import TimeStampedModel
from autoslug import AutoSlugField
# Create your models here.


class Services(TimeStampedModel):

    service_name = models.CharField(max_length=50, db_index=True)
    is_active = models.BooleanField(default=True)
    slug = AutoSlugField(max_length=20, populate_from='service_name')

    objects = models.Manager

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Service'

    def __str__(self):
        return self.service_name


class Designation(TimeStampedModel):

    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='designations')
    name = models.CharField(max_length=50, db_index=True)
    is_active = models.BooleanField(default=True)
    slug = AutoSlugField(max_length=50, populate_from='name')

    objects = models.Manager

    class Meta:
        verbose_name = 'Designation'
        verbose_name_plural = 'Designation'

    def __str__(self):
        return self.name


class Banks(TimeStampedModel):

    bank_name = models.CharField(unique=True, max_length=100)
    slug = AutoSlugField(populate_from='bank_name')
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Bank'
        verbose_name_plural = 'Bank'

    def __str__(self):
        return self.bank_name

    def save(self, *args, **kwargs):
        self.bank_name = self.bank_name.upper()
        super().save(*args, **kwargs)


class SalaryComponents(models.Model):

    Earnings = 'earnings'
    Deductions = 'deductions'

    TYPE_CHOICES = (
        (Earnings, 'Earnings'),
        (Deductions, 'Deductions')
    )

    name = models.CharField(max_length=20)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)

    def __str__(self):
        return self.name


class SalaryFormulas(models.Model):
    pass


class ClientSalaryStructure(models.Model):
    pass
