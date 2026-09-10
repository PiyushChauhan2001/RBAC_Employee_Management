from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Employee, Department
from accounts.serializers import UserSerializer

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(source="employees.count", read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "description", "employee_count"]


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id", "user", "employee_id", "department", "department_name", "designation",
            "phone", "address", "date_of_joining", "date_of_birth", "salary", "status",
            "manager", "manager_name", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.user.get_full_name() or obj.manager.user.username
        return None


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Creates a User + linked Employee profile in one request (Admin/HR only)."""

    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices, write_only=True, default=User.Role.EMPLOYEE)

    class Meta:
        model = Employee
        fields = [
            "id", "username", "email", "first_name", "last_name", "password", "role",
            "employee_id", "department", "designation", "phone", "address",
            "date_of_joining", "date_of_birth", "salary", "status", "manager",
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.pop("username"),
            email=validated_data.pop("email"),
            first_name=validated_data.pop("first_name"),
            last_name=validated_data.pop("last_name", ""),
            password=validated_data.pop("password"),
            role=validated_data.pop("role"),
        )
        employee = Employee.objects.create(user=user, **validated_data)
        return employee

    def to_representation(self, instance):
        return EmployeeSerializer(instance, context=self.context).data
