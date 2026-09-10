from django.utils import timezone
from rest_framework import serializers
from .models import LeaveRequest, LeaveType


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "max_days_per_year", "description"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_code = serializers.CharField(source="employee.employee_id", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    total_days = serializers.IntegerField(read_only=True)
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id", "employee", "employee_name", "employee_code", "leave_type", "leave_type_name",
            "start_date", "end_date", "total_days", "reason", "status", "applied_on",
            "reviewed_by", "reviewed_by_name", "reviewed_on", "review_comment",
        ]
        read_only_fields = [
            "id", "status", "applied_on", "reviewed_by", "reviewed_on", "employee",
        ]

    def get_employee_name(self, obj):
        return obj.employee.user.get_full_name() or obj.employee.user.username

    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None

    def validate(self, attrs):
        start = attrs.get("start_date") or getattr(self.instance, "start_date", None)
        end = attrs.get("end_date") or getattr(self.instance, "end_date", None)
        if start and end:
            if end < start:
                raise serializers.ValidationError("End date cannot be before the start date.")
            if start < timezone.localdate() and self.instance is None:
                raise serializers.ValidationError("Cannot apply for leave in the past.")
        return attrs


class LeaveReviewSerializer(serializers.Serializer):
    """Used by Admin/HR to approve or reject a pending request."""

    action = serializers.ChoiceField(choices=["APPROVE", "REJECT"])
    comment = serializers.CharField(required=False, allow_blank=True, max_length=255)
