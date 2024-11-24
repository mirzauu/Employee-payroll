from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm as CorePasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth import forms as auth_forms
from .utils import generate_user

User = get_user_model()


class SingUpForm(UserCreationForm):

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if first_name and not first_name.isalpha():
            raise forms.ValidationError("First Name must be String")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last Name must be String")
        return last_name

    first_name = forms.CharField(
        max_length=30,
        required=True
    )

    last_name = forms.CharField(
        max_length=20,
        required=True
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'email': 'Email',
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'password1': 'Password',
            'password2': 'Confirm Password'
        }

    def __init__(self, *args, **kwargs):
        super(SingUpForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-lg'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = generate_user()
        if commit:
            user.save()
        return user
        

