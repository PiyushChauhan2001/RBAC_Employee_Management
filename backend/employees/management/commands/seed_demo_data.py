import datetime
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from employees.models import Department, Employee
from leaves.models import LeaveType

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds demo departments, leave types, and admin/HR/employee accounts for local testing."

    def handle(self, *args, **options):
        eng, _ = Department.objects.get_or_create(name="Engineering", defaults={"description": "Product & platform engineering"})
        hr_dept, _ = Department.objects.get_or_create(name="Human Resources", defaults={"description": "People operations"})

        for name, days in [("Annual Leave", 18), ("Sick Leave", 10), ("Casual Leave", 8)]:
            LeaveType.objects.get_or_create(name=name, defaults={"max_days_per_year": days})

        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin", email="admin@example.com", password="AdminPass123!", role=User.Role.ADMIN,
                first_name="System", last_name="Admin",
            )
            self.stdout.write(self.style.SUCCESS("Created admin: admin / AdminPass123!"))
        else:
            admin = User.objects.get(username="admin")

        if not User.objects.filter(username="hr_manager").exists():
            hr_user = User.objects.create_user(
                username="hr_manager", email="hr@example.com", password="HrPass123!", role=User.Role.HR,
                first_name="Hana", last_name="Ruiz",
            )
            Employee.objects.create(
                user=hr_user, employee_id="EMP-0001", department=hr_dept, designation="HR Manager",
                date_of_joining=datetime.date(2022, 3, 1), status=Employee.Status.ACTIVE,
            )
            self.stdout.write(self.style.SUCCESS("Created HR: hr_manager / HrPass123!"))

        if not User.objects.filter(username="jdoe").exists():
            emp_user = User.objects.create_user(
                username="jdoe", email="jdoe@example.com", password="EmployeePass123!", role=User.Role.EMPLOYEE,
                first_name="Jamie", last_name="Doe",
            )
            Employee.objects.create(
                user=emp_user, employee_id="EMP-0002", department=eng, designation="Software Engineer",
                date_of_joining=datetime.date(2023, 6, 15), status=Employee.Status.ACTIVE,
                phone="+15551234567",
            )
            self.stdout.write(self.style.SUCCESS("Created employee: jdoe / EmployeePass123!"))

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
