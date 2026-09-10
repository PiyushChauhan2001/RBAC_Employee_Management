from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from employees.models import Employee
from attendance.models import Attendance

User = get_user_model()


class AttendanceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="john", email="john@test.com", password="Password123!", role=User.Role.EMPLOYEE
        )
        self.employee = Employee.objects.create(
            user=self.user,
            employee_id="EMP-001",
            designation="Analyst",
            date_of_joining=date(2024, 1, 1),
        )

    def test_check_in_and_check_out_flow(self):
        self.client.force_authenticate(user=self.user)

        # Check in
        response = self.client.post("/api/attendance/check-in/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["check_in"])

        # Duplicate check in should fail
        response_dup = self.client.post("/api/attendance/check-in/")
        self.assertEqual(response_dup.status_code, status.HTTP_400_BAD_REQUEST)

        # Check out
        response_out = self.client.post("/api/attendance/check-out/")
        self.assertEqual(response_out.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response_out.data["check_out"])

    def test_my_history(self):
        self.client.force_authenticate(user=self.user)
        Attendance.objects.create(
            employee=self.employee,
            date=timezone.localdate(),
            status=Attendance.Status.PRESENT,
        )
        response = self.client.get("/api/attendance/my-history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
