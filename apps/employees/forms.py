# forms.py
from django import forms

class EmployeeUploadForm(forms.Form):
    file = forms.FileField()
