from datetime import datetime

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Attendance
from .serializers import AttendanceSerializer
from employees.models import Employee


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Admin/HR: see and manage attendance for every employee.
    Employee: see only their own history; self-service check-in/check-out actions.
    Direct create/update/delete of arbitrary records is restricted to Admin/HR —
    employees use the check_in / check_out actions instead, which only ever touch
    their own record for the current day.
    """

    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "date", "status"]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related("employee__user")
        if user.is_admin_or_hr:
            return qs
        return qs.filter(employee__user=user)

    def get_permissions(self):
        if self.action in ("check_in", "check_out", "my_history"):
            return [permissions.IsAuthenticated()]
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), _IsAdminOrHRForWrite()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "No employee profile linked to this account."}, status=404)

        today = timezone.localdate()
        now = timezone.localtime().time()
        record, created = Attendance.objects.get_or_create(
            employee=employee, date=today,
            defaults={"check_in": now, "status": Attendance.Status.PRESENT},
        )
        if not created and record.check_in:
            return Response({"detail": "Already checked in today."}, status=status.HTTP_400_BAD_REQUEST)
        if not created:
            record.check_in = now
            record.status = Attendance.Status.PRESENT
            record.save()
        return Response(AttendanceSerializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="check-out")
    def check_out(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "No employee profile linked to this account."}, status=404)

        today = timezone.localdate()
        try:
            record = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({"detail": "You haven't checked in today."}, status=status.HTTP_400_BAD_REQUEST)

        if record.check_out:
            return Response({"detail": "Already checked out today."}, status=status.HTTP_400_BAD_REQUEST)

        record.check_out = timezone.localtime().time()
        record.save()
        return Response(AttendanceSerializer(record).data)

    @action(detail=False, methods=["get"], url_path="my-history")
    def my_history(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "No employee profile linked to this account."}, status=404)
        records = Attendance.objects.filter(employee=employee).order_by("-date")
        page = self.paginate_queryset(records)
        serializer = AttendanceSerializer(page or records, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class _IsAdminOrHRForWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_or_hr)
