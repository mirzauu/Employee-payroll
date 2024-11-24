from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.account.models import Account
from rest_framework.exceptions import ValidationError
from apps.account.utils import generate_user
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import Group


User = get_user_model()


def validate_name(value):
    if value and not value.isalpha():
        raise ValidationError("No Numbers are Allowed")
    return value


class RegisterUserSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=30, required=True,
                                   style={
                                       'input_type': 'text',
                                       'placeholder': 'Last Name',
                                   })
    first_name = serializers.CharField(max_length=20, required=True, validators=[validate_name],
                                       style={
                                           'input_type': 'text',
                                           'placeholder': 'Last Name',
                                       })
    last_name = serializers.CharField(max_length=20, required=True, validators=[validate_name],
                                      style={
                                          'input_type': 'text',
                                          'placeholder': 'Last Name',
                                      })
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={
            'input_type': 'password',
            'placeholder': 'Enter your password',
            'class': 'custom-password-field',
        }
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={
            'input_type': 'password',
            'placeholder': 'Enter your password',
            'class': 'custom-password-field',
        }
    )

    def validate(self, attrs):
        email = attrs.get('email')
        if email and Account.objects.filter(email=email).exists():
            raise ValidationError("User with this email already exists")

        for field_name, field_value in attrs.items():
            if field_value is None:
                raise ValidationError(f"{field_name} is required")

        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        user = Account.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=generate_user()
        )
        user.set_password(validated_data['password'])
        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=30, required=True,
                                   style={
                                       'input_type': 'text',
                                       'placeholder': 'Enter your Email',
                                   })
    password = serializers.CharField(max_length=30, required=True,
                                     style={
                                        'input_type': 'password',
                                        'placeholder': 'Enter your password',
                                        'class': 'custom-password-field',
                                     })


class SendPasswordResetEmailSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=30, write_only=True,
                                   required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if email is not None:
            if Account.objects.filter(email=email).exists():
                user = Account.objects.get(email=email)
                uid = urlsafe_base64_encode(force_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                link = 'http://127.0.0.1:8000/reset/' + uid + '/' + token
                data = {
                    'subject': 'Reset Your Password',
                    'body': '',
                    'to_email': user.email
                }
                return attrs
            else:
                raise serializers.ValidationError('You are not a Registered User')


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name', 'image', 'groups')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['groups'] = [group.name for group in instance.groups.all()]
        return represent


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['permissions'] = [{'label': x.name, 'value': x.id} for x in instance.permissions.all()]
        return represent

