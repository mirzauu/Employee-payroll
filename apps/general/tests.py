from django.test import TestCase
from .models import Services
# Create your tests here.


class ServiceTestCase(TestCase):

    def test_services(self):
        service = Services.objects.create(name="House Keeping", is_active=True)
        self.assertEqual(str(service), 'House Keeping')
        self.assertTrue(isinstance(service, Services))
