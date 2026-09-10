from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from employees.models import Employee
from leaves.models import LeaveType, LeaveRequest

User = get_user_model()


class LeavesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.hr = User.objects.create_user(
            username="hr_user", email="hr@test.com", password="Password123!", role=User.Role.HR
        )
        self.emp_user = User.objects.create_user(
            username="emp_user", email="emp@test.com", password="Password123!", role=User.Role.EMPLOYEE
        )
        self.employee = Employee.objects.create(
            user=self.emp_user,
            employee_id="EMP-005",
            designation="Specialist",
            date_of_joining=date(2024, 1, 1),
        )
        self.leave_type = LeaveType.objects.create(name="Annual Leave", max_days_per_year=14)

    def test_apply_and_review_leave(self):
        # Employee applies for leave
        self.client.force_authenticate(user=self.emp_user)
        today = timezone.localdate()
        payload = {
            "leave_type": self.leave_type.id,
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat(),
            "reason": "Vacation trip",
        }
        response = self.client.post("/api/leaves/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        leave_id = response.data["id"]

        # HR reviews leave request
        self.client.force_authenticate(user=self.hr)
        review_payload = {"action": "APPROVE", "comment": "Have fun!"}
        review_resp = self.client.post(f"/api/leaves/{leave_id}/review/", review_payload)
        self.assertEqual(review_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(review_resp.data["status"], "APPROVED")

    def test_user_without_employee_profile_cannot_create_leave(self):
        # HR user without employee profile attempts to create leave
        self.client.force_authenticate(user=self.hr)
        today = timezone.localdate()
        payload = {
            "leave_type": self.leave_type.id,
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat(),
            "reason": "Vacation trip",
        }
        response = self.client.post("/api/leaves/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
