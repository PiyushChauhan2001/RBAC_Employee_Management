from django.utils import timezone
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LeaveRequest, LeaveType
from .serializers import LeaveRequestSerializer, LeaveReviewSerializer, LeaveTypeSerializer
from employees.models import Employee
from accounts.permissions import IsAdminOrHR, ReadOnlyOrAdminHR


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [ReadOnlyOrAdminHR]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    Employee: apply for leave, view/cancel their own pending requests.
    Admin/HR: view every request, approve/reject, and manage leave records.
    """

    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "leave_type", "employee"]

    def get_queryset(self):
        user = self.request.user
        qs = LeaveRequest.objects.select_related("employee__user", "leave_type", "reviewed_by")
        if user.is_admin_or_hr:
            return qs
        return qs.filter(employee__user=user)

    def get_permissions(self):
        if self.action in ("destroy",):
            return [IsAdminOrHR()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Employees can only ever file leave requests against their own profile.
        try:
            employee = self.request.user.employee_profile
        except Employee.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "No employee profile linked to this account."})
        serializer.save(employee=employee, status=LeaveRequest.Status.PENDING)


    def perform_update(self, serializer):
        instance = self.get_object()
        if not self.request.user.is_admin_or_hr and instance.status != LeaveRequest.Status.PENDING:
            raise permissions.PermissionDenied("Only pending requests can be edited.")
        serializer.save()

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        leave = self.get_object()
        if leave.employee.user != request.user and not request.user.is_admin_or_hr:
            return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)
        if leave.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "Only pending requests can be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        leave.status = LeaveRequest.Status.CANCELLED
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=["post"], url_path="review", permission_classes=[IsAdminOrHR])
    def review(self, request, pk=None):
        leave = self.get_object()
        if leave.status != LeaveRequest.Status.PENDING:
            return Response({"detail": "This request has already been reviewed."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LeaveReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        leave.status = (
            LeaveRequest.Status.APPROVED
            if serializer.validated_data["action"] == "APPROVE"
            else LeaveRequest.Status.REJECTED
        )
        leave.review_comment = serializer.validated_data.get("comment", "")
        leave.reviewed_by = request.user
        leave.reviewed_on = timezone.now()
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=False, methods=["get"], url_path="my-requests")
    def my_requests(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "No employee profile linked to this account."}, status=404)
        records = LeaveRequest.objects.filter(employee=employee).order_by("-applied_on")
        page = self.paginate_queryset(records)
        serializer = LeaveRequestSerializer(page or records, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
