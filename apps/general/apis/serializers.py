import re
from rest_framework import serializers
from apps.general.models import Services, Designation, Banks
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.core.validators import FileExtensionValidator

def validate_name(value):
    if not isinstance(value, str):
        raise ValidationError("No Numbers are Allowed")
    return value


class ServiceOptionSerializer(serializers.Serializer):

    value = serializers.PrimaryKeyRelatedField(source='pk', read_only=True)
    label = serializers.CharField(source='service_name', read_only=True)


class ServiceSerializer(serializers.Serializer):

    id = serializers.PrimaryKeyRelatedField(source='pk', read_only=True)
    service_name = serializers.CharField(max_length=20, required=True, validators=[validate_name])
    is_active = serializers.BooleanField(default=True)

    def validate_service_name(self, value):
        if not value:
            raise ValidationError("Service Name cannot be Empty")
        elif value and not re.match(r'^[a-zA-Z\s]*$', value):
            raise serializers.ValidationError("Service Name Cannot Consist of Number and Special Char")
        return value

    def validate(self, data):
        service_name = data.get('service_name')
        if Services.objects.filter(service_name=service_name).exists():
            raise ValidationError("Service Already Exists")
        return data

    def create(self, validated_data):
        service = Services.objects.create(service_name=validated_data['service_name'])
        return service

    def update(self, instance, validated_data):
        instance.service_name = validated_data.get('service_name', instance.service_name)
        instance.save()
        return instance


class DesignationSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    service = serializers.PrimaryKeyRelatedField(queryset=Services.objects.only('id'))
    name = serializers.CharField(max_length=20, required=True, validators=[validate_name])
    is_active = serializers.BooleanField(default=True)

    def validate_service(self, value):
        if not value:
            raise ValidationError("Service Field cannot be Empty")
        return value

    def validate_name(self, value):
        if not value:
            raise ValidationError("Designation Name cannot be Empty")
        elif value and not re.match(r'^[a-zA-Z\s]*$', value):
            raise serializers.ValidationError("Designation Name Cannot Consist of Number and Special Char")
        return value

    def validate(self, attrs):
        name = attrs.get('name')
        if Designation.objects.filter(name=name).exists():
            raise ValidationError("Designation Already Exists")
        return attrs

    def create(self, validated_data):
        try:
            designation = Designation.objects.create(service=validated_data['service'], name=validated_data['name'])
            return designation
        except Exception as e:
            raise ValidationError({"success": False, "data": str(e)})

    def update(self, instance, validated_data):
        try:
            service = Services.objects.get(id=validated_data['service'].id)
            instance.service = service
            instance.name = validated_data['name']
            instance.save()
            return instance
        except Exception as e:
            raise ValidationError({"success": False, "data": str(e)})

    def to_representation(self, instance):
        respresent = super().to_representation(instance)
        respresent['service'] = instance.service.service_name
        return respresent


class EmployeeDesignation(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = ['id', 'name']


class BankOptionSerializer(serializers.ModelSerializer):

    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='bank_name')

    class Meta:
        model = Banks
        fields = ('value', 'label')


class DesignationOptionSerializer(serializers.ModelSerializer):

    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='name')

    class Meta:
        model = Banks
        fields = ('value', 'label')


class BankSerializer(serializers.Serializer):

    bank_name = serializers.CharField(required=True)
    
    def create(self, validated_data):
        bank_name = validated_data.get('bank_name')
        try:
            return Banks.objects.create(bank_name=bank_name)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower():
                raise ValidationError({"error": "Bank Already Existes"})
            else:
                raise ValidationError(str(e))


class UploadFileSerializer(serializers.Serializer):

    choices = (
        ('Employee', 'Employee'),
        ('Bank', 'Bank')
    )

    upload_type = serializers.ChoiceField(choices=choices)
    file = serializers.FileField(required=True, validators=[FileExtensionValidator(allowed_extensions=['xlsx'])])