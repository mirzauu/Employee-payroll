import re
import json
from rest_framework import serializers
from apps.clients.models import Client, Rule, ClientSalarySettings, EarningsComponent, DeductionComponent
from apps.employees.models import Employee
from apps.general.models import Services, Designation
from apps.employees.apis.serializers import EmployeeListSerializer
from apps.employees.models import ShiftEmployee
from apps.employees.models import ShiftEmployee, EmployeeHistory
from django.db import transaction
from datetime import datetime, timedelta
from rest_framework.exceptions import ValidationError
from apps.general.apis.serializers import ServiceOptionSerializer, DesignationOptionSerializer
from django.conf import settings
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist


class ClientEmployeeList(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'designation', 'phone_no']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['designation'] = instance.designation.name
        return response


class ClientSerializer(serializers.ModelSerializer):

    employee_company = ClientEmployeeList(many=True, read_only=True, required=False)
    service = serializers.PrimaryKeyRelatedField(queryset=Services.objects.all(), many=True)
    designation = serializers.PrimaryKeyRelatedField(queryset=Designation.objects.all(), many=True)

    class Meta:
        model = Client
        exclude = ('created', 'modified')

    def validate_client_name(self, value):
        if not value:
            raise serializers.ValidationError("Client Name Field Cannot Be Empty")
        elif value and not re.match(r'^[a-zA-Z\s]*$', value):
            raise serializers.ValidationError("Client Name Cannot Consist of Number and Special Char")
        return value

    def validate_client_phone(self, value):
        phone_number_pattern = re.compile(r'^\d{10}$')
        instance = self.instance
        if not instance and Client.objects.filter(client_phone=value).exists():
            raise serializers.ValidationError("Client Phone Number Already Exists")
        elif value and len(value) < 10 or len(value) > 10:
            raise serializers.ValidationError({"message": "Invalid phone number format. Please enter a 10-digit number."})
        elif value and not phone_number_pattern.match(value):
            raise serializers.ValidationError(
                {"message": "Phone Number cannot contain Alphabets or Special Charaters"})
        return value

    def validate_client_gst(self, value):
        if value and value != 'null':
            if len(value) != 15:
                raise serializers.ValidationError("Gst Number Should have 15 Characters")
            if not re.match(r'^[a-zA-Z0-9]*$', value):
                raise serializers.ValidationError("Gst Number should contain only alphanumeric characters")
            return value

    def validate_lut_tenure(self, value):
        if value:
            if not re.match(r'^[a-zA-Z0-9\s]*$', value):
                raise serializers.ValidationError("Lut Number should contain only alphanumeric characters")
            return value

    def validate_client_city(self, value):
        if not value:
            raise serializers.ValidationError("City Fields Cannot be Empty")
        if not re.match(r'^[a-zA-Z\s]*$', value):
            raise serializers.ValidationError("City name should contain only alphabets and spaces")
        return value

    def validate_client_pincode(self, attrs):
        pincode_pattern = re.compile(r'^\d{6}$')
        if attrs and len(attrs) != 6:
            raise serializers.ValidationError("Please Enter a valid Pincode")
        if attrs and not pincode_pattern.match(attrs):
            raise serializers.ValidationError("Pincode must be Numbers")
        return attrs

    def validate_billing_type(self, value):
        if not value:
            raise serializers.ValidationError("Billing Type cannot be Empty")
        return value

    def validate_client_sector(self, value):
        if not value:
            raise serializers.ValidationError("Billing Type cannot be Empty")
        return value

    def validate_service(self, value):
        if not value:
            raise serializers.ValidationError("Service Field cannot be empty")
        return value

    def validate_designation(self, value):
        if not value:
            raise serializers.ValidationError("Designation Field cannot be empty")
        return value

    def validate(self, attrs):
        instance = self.instance
        client_phone = attrs.get('client_phone')
        if not self.instance and Client.objects.filter(client_phone=client_phone,).exists():
            raise ValidationError("Phone Number is Already Present")
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request', None)
        hide_relationship = self.context.get('hide_relationship', True)
        if hide_relationship and 'employee_company' in self.fields:
            del self.fields['employee_company']
        represent = super().to_representation(instance)
        represent['service'] = [{'value': value.id, 'label': value.service_name} for value in instance.service.all()]
        represent['designation'] = [{'value': value.id, 'label': value.name} for value in instance.designation.all()]
        if instance.client_logo:
            media_url = request.build_absolute_uri(static('images/'))
            represent['client_logo'] = f"{media_url}{instance.client_logo.name}"
        return represent


class ClientListSerializer(serializers.Serializer):

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    sector = serializers.CharField(read_only=True)
    client_phone = serializers.CharField(read_only=True)
    client_email = serializers.EmailField(read_only=True)
    client_logo = serializers.SerializerMethodField()
    client_employees = serializers.SerializerMethodField()
    payroll_id = serializers.SerializerMethodField()

    def get_client_logo(self, obj):
        if obj.client_logo:
            # Assuming 'images' is the media URL pattern defined in your Django project
            media_url = self.context['request'].build_absolute_uri(static('images/'))
            return f"{media_url}{obj.client_logo.name}"
        return None

    def get_client_employees(self, instance):
        emp_count = Employee.objects.filter(current_company=instance.id).count()
        return emp_count

    def get_payroll_id(self, instance):
        try:
            payroll = ClientSalarySettings.objects.get(company=instance)
            return payroll.id
        except Exception as e:
            return None

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['client_employees'] = self.get_client_employees(instance)
        represent['payroll_id'] = self.get_payroll_id(instance.id)
        return represent


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = ['id', 'service_name']


class ShiftEmpSerializer(serializers.ModelSerializer):

    Permenent = 'Permenent'
    Temporary = 'Temporary'

    shift_choice = (
        (Permenent, 'Permenent'),
        (Temporary, 'Temporary')
    )

    shift_type = serializers.ChoiceField(choices=shift_choice, write_only=True)

    class Meta:
        model = ShiftEmployee
        fields = '__all__'

    def validate(self, attrs):
        emp_id = attrs.get('emp_id')
        instance = ShiftEmployee.objects.filter(emp_id=emp_id, is_active=True)
        if instance:
            raise ValidationError({'error': "Employee Already On a Shift Please Change It"})
        return attrs

    def save(self, **kwargs):
        shift_type = self.validated_data.pop('shift_type')
        emp_instance = self.validated_data.get('emp_id')
        com_instance = self.validated_data.get('shifted_company')
        try:
            data = super().save(**kwargs)
            emp_instance.current_company = com_instance
            emp_instance.save()
            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))


class EmployeeCompanyEdit(serializers.Serializer):

    emp_id = serializers.CharField(required=True, write_only=True)
    from_date = serializers.DateField()
    shifted_company = serializers.IntegerField(write_only=True, required=True)

    def save(self, **kwargs):
        # shift_type = self.validated_data.pop('shift_type')
        emp_id = self.validated_data.get('emp_id')
        company_id = self.validated_data.get('shifted_company')
        try:
            emp_instance = Employee.objects.get(emp_id=emp_id)
            client_instance = Client.objects.get(id=company_id)
            emp_history = EmployeeHistory.objects.create(emp_id=emp_instance,
                                                         joined_date=self.validated_data.get('from_date'),
                                                         prev_company=emp_instance.current_company,
                                                         last_worked=self.validated_data.get('from_date') - timedelta(days=1))
            emp_instance.current_company = client_instance
            emp_instance.joining_date = self.validated_data.get('from_date')
            emp_instance.save()
            return emp_history
        except Exception as e:
            raise serializers.ValidationError(str(e))


class clientOptionSerializer(serializers.ModelSerializer):

    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='client_name')

    class Meta:
        model = Client
        fields = ('value', 'label')


class ShiftEmpListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShiftEmployee
        fields = ['id', 'emp_id', 'prev_company', 'shifted_company', 'from_date', 'to_date']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['emp_id'] = instance.emp_id.name
        response['prev_company'] = instance.prev_company.client_name
        response['shifted_company'] = instance.shifted_company.client_name
        return response


class GenerateDataSerializer(serializers.Serializer):

    pass


class RuleSerializer(serializers.ModelSerializer):

    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='rules')

    class Meta:
        model = Rule
        fields = ['value', 'label']


class ClientSalarySerializer(serializers.ModelSerializer):

    associated_structure = serializers.SerializerMethodField()

    def get_associated_structure(self, obj):
        count = EarningsComponent.objects.filter(client_settings__company__client_name=obj).count()
        return count

    class Meta:
        model = ClientSalarySettings
        exclude = ('created', 'modified')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['company'] = instance.company.client_name
        represent['client_id'] = instance.company.id
        if self.context['settings']:
            represent['rule'] = {"label": instance.rule.rules, "value": instance.rule.id}
        else:
            represent['associated_structures'] = self.get_associated_structure(represent['company'])
            represent['rule'] = instance.rule.rules
        return represent


class ClientSalaryOptionSerializer(serializers.ModelSerializer):

    value = serializers.IntegerField(source='id')
    label = serializers.CharField(source='company.client_name')

    class Meta:
        model = ClientSalarySettings
        fields = ['value', 'label']


class SalaryComponentSerializer(serializers.Serializer):

    id = serializers.IntegerField(source='pk')
    designation = serializers.CharField(source='employee_type.name')
    salary = serializers.IntegerField(source='basic_vda')


class DeductionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeductionComponent
        fields = ('professional_tax', 'lwf_amount', 'canteen', 'swf', 'deduction_components')


class SalaryStructureSerializer(serializers.ModelSerializer):
    deductions = DeductionSerializer(many=True, required=False)

    class Meta:
        model = EarningsComponent
        exclude = ('created', 'modified')

    def create(self, validated_data):
        deductions = validated_data.pop('deductions', [])
        earnings = EarningsComponent.objects.create(**validated_data)
        for deduction in deductions:
            DeductionComponent.objects.create(earnings=earnings, **deduction)
        return earnings

    def update(self, instance, validated_data):
        deductions = validated_data.pop('deductions', [])
        ints = None
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for deduction_data in deductions:
            try:
                deduction_component = DeductionComponent.objects.get(earnings=instance)
                for key, value in deduction_data.items():
                    setattr(deduction_component, key, value)
                deduction_component.save()
            except DeductionComponent.DoesNotExist:
                DeductionComponent.objects.create(earnings=instance, **deduction_data)
        return instance

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['client_settings_name'] = f"{instance.client_settings.company.client_name} - settings"
        represent['employee_type_name'] = instance.employee_type.name
        return represent
