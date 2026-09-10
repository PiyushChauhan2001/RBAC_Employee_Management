from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from employees.models import Department, Employee

User = get_user_model()


class EmployeesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin", email="admin@test.com", password="Password123!", role=User.Role.ADMIN
        )
        self.emp_user = User.objects.create_user(
            username="emp1", email="emp1@test.com", password="Password123!", role=User.Role.EMPLOYEE
        )
        self.department = Department.objects.create(name="Engineering", description="Tech dept")
        self.employee = Employee.objects.create(
            user=self.emp_user,
            employee_id="EMP-101",
            department=self.department,
            designation="Developer",
            date_of_joining=date(2024, 1, 1),
        )

    def test_employee_me_endpoint(self):
        self.client.force_authenticate(user=self.emp_user)
        response = self.client.get("/api/employees/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee_id"], "EMP-101")
        self.assertEqual(response.data["department_name"], "Engineering")

    def test_admin_create_employee(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "username": "new_dev",
            "email": "newdev@test.com",
            "first_name": "New",
            "last_name": "Dev",
            "password": "Password123!",
            "role": "EMPLOYEE",
            "employee_id": "EMP-102",
            "department": self.department.id,
            "designation": "Junior Engineer",
            "date_of_joining": "2024-03-01",
        }
        response = self.client.post("/api/employees/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="new_dev").exists())
        self.assertTrue(Employee.objects.filter(employee_id="EMP-102").exists())

    def test_employee_cannot_create_employee(self):
        self.client.force_authenticate(user=self.emp_user)
        payload = {"employee_id": "EMP-999"}
        response = self.client.post("/api/employees/", payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
