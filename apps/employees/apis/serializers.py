from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ..models import Employee, EmployeeBank, EmployeeLoan, LoanHistory, EmployeeAttendance, Payslip
from PIL import Image as PILImage
import re
from apps.general.apis.serializers import ServiceSerializer, EmployeeDesignation, DesignationSerializer
from django.templatetags.static import static


def _image_format_validation(attrs):
    if attrs is not None:
        try:
            image = PILImage.open(attrs)
            image_format = image.format.lower()
            if image_format in ['png', 'jpge', 'jpg']:
                return attrs
        except Exception as e:
            raise ValidationError({'error': f'Invalid image format for {image}'})
    elif attrs is None:
        return attrs


class EmployeeBankSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeBank
        fields = ('bank', 'accountNumber', 'ifscCode')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['bank'] = instance.bank.bank_name
        return response


class EmployeeBankIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeBank
        fields = ('bank', 'accountNumber', 'ifscCode')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['bank'] = {'value': instance.bank.id, 'label': instance.bank.bank_name}
        return response


class EmployeeSerializer(serializers.ModelSerializer):

    emp_bank = EmployeeBankIdSerializer(required=False, many=True, read_only=True)
    profile_img = serializers.ImageField(required=False, validators=[_image_format_validation])
    pcc_image = serializers.ImageField(required=False, validators=[_image_format_validation])
    aadhar_image = serializers.ImageField(required=False, validators=[_image_format_validation])
    is_active = serializers.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        request = kwargs['context']['request'] if 'context' in kwargs and 'request' in kwargs['context'] else None
        if request and (request.method == "PUT" or request.method == "PATCH"):
            self.Meta.exclude = ('created', 'modified')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Employee
        exclude = ('created', 'modified')

    def validate_emp_id(self, value):
        if not value:
            raise serializers.ValidationError("Emp Id cannot be Empty")
        elif not re.match(r'[0-9]*$', value):
            raise serializers.ValidationError("Emp Id cannot be Character or Special Character")
        return value

    def validate_name(self, value):
        if any(char.isdigit() for char in value):
            raise ValidationError("No Numbers Are Allowed")
        return value

    def validate_phone_no(self, value):
        phone_number_pattern = re.compile(r'^\d{10}$')
        if not value:
            raise serializers.ValidationError("Phone Number Cannot be Empty")
        elif len(value) < 10 or len(value) > 10:
            raise serializers.ValidationError({"message": "Invalid phone number format. Please enter a 10-digit number."})
        elif not phone_number_pattern.match(value):
            raise serializers.ValidationError(
                {"message": "Phone Number cannot contain Alphabets or Special Charaters"})
        return value

    def validate_whatsappNum(self, value):
        phone_number_pattern = re.compile(r'^\d{10}$')
        if not value:
            raise serializers.ValidationError("Whatsapp Number Cannot be Empty")
        elif len(value) < 10 or len(value) > 10:
            raise serializers.ValidationError({"message": "Invalid phone number format. Please enter a 10-digit number."})
        elif not phone_number_pattern.match(value):
            raise serializers.ValidationError(
                {"message": "Phone Number cannot contain Alphabets or Special Charaters"})
        return value

    def validate_aadhar(self, value):
        if len(value) < 12:
            raise ValidationError("Please Enter the Correct Aadhar Number")
        elif value.isalpha():
            raise ValidationError("No Characters are Allowed")
        return value

    def validate_address(self, value):
        if not value:
            raise serializers.ValidationError("Address Field cannot be Empty")
        return value

    def validate_uanNumber(self, value):
        instance = self.instance
        if not instance and Employee.objects.filter(uanNumber=value).exists():
            raise serializers.ValidationError("uanNumber already Exists")
        elif value and len(value) != 12:
            raise serializers.ValidationError("uanNumber Only Contains 12 Numbers")
        elif not re.match(r'[0-9]*$', value):
            raise serializers.ValidationError("UanNumber Cannot Contain Character or Special Charater")
        return value

    def validate(self, attrs):
        emp_id = attrs.get('emp_id')
        instance = self.instance
        if not instance:
            if Employee.objects.filter(emp_id=emp_id).exists():
                raise ValidationError({'error': "employee Id already Exixts"})
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request', None)
        response = super().to_representation(instance)
        response['designation'] = {
            "id": instance.designation.pk,
            "name": instance.designation.name
        }
        response['current_company'] = {
            "id": instance.current_company.pk,
            "name": instance.current_company.client_name
        }
        media_url = request.build_absolute_uri(static('images/'))
        if instance.profile_img:
            response['profile_img'] = f"{media_url}{instance.profile_img.name}"
        if instance.pcc_image:
            response['pcc_image'] = f"{media_url}{instance.pcc_image.name}"
        if instance.aadhar_image:
            response['aadhar_image'] = f"{media_url}{instance.aadhar_image.name}"
        return response


class EmployeeListSerializer(serializers.Serializer):

    name = serializers.CharField(read_only=True)
    emp_id = serializers.CharField(read_only=True)
    phone_no = serializers.CharField(read_only=True)
    designation = serializers.CharField(read_only=True)
    current_company = serializers.SlugRelatedField(read_only=True, slug_field='client_name')
    profile_img = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)

    def get_profile_img(self, obj):
        if obj.profile_img:
            media_url = self.context['request'].build_absolute_uri(static('images/'))
            return f"{media_url}{obj.profile_img.name}"
        return None


class EmployeeCompanyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('emp_id', 'name', 'phone_no', 'bloodGroup', 'joining_date', 'profile_img', 'designation')

    def to_representation(self, instance):
        request = self.context.get('request', None)
        represent = super().to_representation(instance)
        represent['designation'] = instance.designation.name
        if instance.profile_img:
            media_url = request.build_absolute_uri(static('images/'))
            represent['profile_img'] = f"{media_url}{instance.profile_img.name}"
        return represent


class EmployeeBankSerializer(serializers.ModelSerializer):

    def validate_employee(self, value):
        instance = self.instance
        if value and not instance and EmployeeBank.objects.filter(employee=value).exists():
            raise serializers.ValidationError("This Employee Already has Bank Assingned")
        return value

    def validate_accountNumber(self, value):
        if not value:
            raise serializers.ValidationError("Account Number Field Cannot be empty")
        if len(value) < 11 or len(value) > 16:
            raise serializers.ValidationError("Account Number Should have atleast 16 Number")
        if value and not re.match(r'^[0-9]{11,16}$', value):
            raise serializers.ValidationError("Account Number Cannot be String or Special Characters")
        return value

    def validate_ifscCode(self, value):
        if not value:
            raise serializers.ValidationError("Please Enter Bank Ifsc Code")
        if value and not re.match(r'^[a-zA-Z0-9]*$', value):
            raise serializers.ValidationError("Account Number Cannot be String or Special Characters")
        return value

    def validate(self, attrs):
        instance = self.instance
        acc_num = attrs.get('accountNumber')
        if not instance and EmployeeBank.objects.filter(accountNumber=acc_num).exists():
            raise serializers.ValidationError("Account Number Already Exists")
        return attrs

    class Meta:
        model = EmployeeBank
        fields = ('bank', 'employee', 'accountNumber', 'ifscCode')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['bank'] = {"value": instance.bank.id, "label": instance.bank.bank_name}
        response['employee'] = instance.employee.name
        return response


class LoadHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = LoanHistory
        exclude = ('created', 'modified')


class EmployeeLoanListSerializer(serializers.ModelSerializer):

    emp_id = serializers.IntegerField(source='employee.emp_id', read_only=True)
    profile_img = serializers.ImageField(source='employee.profile_img', read_only=True)
    name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = EmployeeLoan
        fields = ['id', 'profile_img', 'emp_id', 'name', 'issued_date', 'amount', 'is_active']


class EmployeeLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLoan
        fields = ['employee', 'amount', 'deduction_amount', 'issued_date']

    def create(self, validated_data):
        validated_data['balance_amount'] = validated_data['amount']
        return super().create(validated_data)


class EmployeeLoanDetailSerializer(serializers.ModelSerializer):

    loan_history = LoadHistorySerializer(many=True)

    class Meta:
        model = EmployeeLoan
        exclude = ('created', 'modified')


class AttendanceListSerializer(serializers.ModelSerializer):

    is_payroll = serializers.SerializerMethodField()
    payroll_id = serializers.SerializerMethodField()

    def get_is_payroll(self, instance):
        try:
            payroll = Payslip.objects.get(emp__emp_id=instance, year=self.context['request'].GET.get('year'),
                                          month=self.context['request'].GET.get('month'))
            return True
        except Exception as e:
            return False

    def get_payroll_id(self, instance):
        try:
            payroll_id = Payslip.objects.get(emp__emp_id=instance, year=self.context['request'].GET.get('year'),
                                             month=self.context['request'].GET.get('month'))
            print(payroll_id)
            return payroll_id.id
        except Exception as e:
            return None

    class Meta:
        model = EmployeeAttendance
        fields = '__all__'

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['is_payroll'] = self.get_is_payroll(represent['employee'])
        represent['payroll_id'] = self.get_payroll_id(represent['employee'])
        represent['emp_id'] = instance.employee.emp_id
        represent['name'] = instance.employee.name
        return represent


class AttendanceSerializer(serializers.ModelSerializer):

    attendance = serializers.JSONField()

    class Meta:
        model = EmployeeAttendance
        exclude = ('created', 'modified')

    def to_representation(self, instance):
        represent = super().to_representation(instance)
        represent['emp_id'] = instance.employee.emp_id
        represent['name'] = instance.employee.name
        del represent['employee']
        return represent


class PayslipListSerializer(serializers.ModelSerializer):

    employee = serializers.CharField(source='emp.name')
    emp_id = serializers.IntegerField(source='emp.emp_id')
    designation = serializers.CharField(source='emp.designation.name')
    net_pay = serializers.CharField(source='grand_total')

    class Meta:
        model = Payslip
        fields = ('id', 'employee', 'emp_id',  'designation', 'net_pay')


class PayslipSerializer(serializers.ModelSerializer):

    employee_id = serializers.CharField(source='emp.emp_id', read_only=True)
    employee_name = serializers.CharField(source='emp.name', read_only=True)
    employee_client = serializers.CharField(source='emp.current_company.client_name', read_only=True)
    employee_designation = serializers.CharField(source='emp.designation.name', read_only=True)
    attendance = serializers.CharField()
    month = serializers.CharField()
    earnings = serializers.JSONField()
    deductions = serializers.JSONField()
    grand_total = serializers.CharField()

    class Meta:
        model = Payslip
        fields = ('employee_id', 'employee_name', 'employee_client', 'employee_designation', 'attendance', 'month',  'earnings', 'deductions',
                  'total_earnings', 'total_deductions', 'grand_total')
