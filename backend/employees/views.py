from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Employee, Department
from .serializers import EmployeeSerializer, EmployeeCreateSerializer, DepartmentSerializer
from accounts.permissions import IsAdminOrHR, ReadOnlyOrAdminHR


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnlyOrAdminHR]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Admin/HR: full CRUD over every employee record.
    Employee (self): read-only access to their own record via /employees/me/.
    """

    queryset = Employee.objects.select_related("user", "department", "manager__user").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["department", "status", "designation"]
    search_fields = ["employee_id", "user__first_name", "user__last_name", "user__email", "designation"]
    ordering_fields = ["employee_id", "date_of_joining", "created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return EmployeeCreateSerializer
        return EmployeeSerializer

    def get_permissions(self):
        if self.action in ("me",):
            return [permissions.IsAuthenticated()]
        return [IsAdminOrHR()]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "No employee profile linked to this account."}, status=404)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
