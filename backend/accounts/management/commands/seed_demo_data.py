from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from employees.models import Department, Employee
from attendance.models import Attendance
from leaves.models import LeaveType, LeaveRequest

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial demo data (departments, leave types, demo users, employees, attendance, leave requests)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        # 1. Departments
        dept_eng, _ = Department.objects.get_or_create(
            name="Engineering", defaults={"description": "Software engineering and technology development."}
        )
        dept_hr, _ = Department.objects.get_or_create(
            name="Human Resources", defaults={"description": "HR management, recruitment, and employee relations."}
        )
        dept_sales, _ = Department.objects.get_or_create(
            name="Sales & Marketing", defaults={"description": "Sales operations, business development, and marketing."}
        )
        dept_ops, _ = Department.objects.get_or_create(
            name="Operations", defaults={"description": "General business operations and logistics."}
        )

        # 2. Leave Types
        lt_annual, _ = LeaveType.objects.get_or_create(
            name="Annual Leave", defaults={"max_days_per_year": 14, "description": "Paid annual vacation days."}
        )
        lt_sick, _ = LeaveType.objects.get_or_create(
            name="Sick Leave", defaults={"max_days_per_year": 10, "description": "Medical and health-related leave."}
        )
        lt_casual, _ = LeaveType.objects.get_or_create(
            name="Casual Leave", defaults={"max_days_per_year": 7, "description": "Short-notice personal leave."}
        )

        # 3. Users & Employees
        # Admin user
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@meridianhr.com",
                "first_name": "System",
                "last_name": "Admin",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("AdminPass123!")
            admin_user.save()

        admin_emp, _ = Employee.objects.get_or_create(
            user=admin_user,
            defaults={
                "employee_id": "EMP-001",
                "department": dept_ops,
                "designation": "Chief Technology Officer",
                "phone": "+1234567890",
                "date_of_joining": date(2023, 1, 15),
                "salary": 120000.00,
                "status": Employee.Status.ACTIVE,
            },
        )

        # HR Manager user
        hr_user, created = User.objects.get_or_create(
            username="hr_manager",
            defaults={
                "email": "hr@meridianhr.com",
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "role": User.Role.HR,
                "is_staff": True,
            },
        )
        if created:
            hr_user.set_password("HrPass123!")
            hr_user.save()

        hr_emp, _ = Employee.objects.get_or_create(
            user=hr_user,
            defaults={
                "employee_id": "EMP-002",
                "department": dept_hr,
                "designation": "HR Operations Director",
                "phone": "+1987654321",
                "date_of_joining": date(2023, 3, 1),
                "salary": 95000.00,
                "status": Employee.Status.ACTIVE,
                "manager": admin_emp,
            },
        )

        # Regular Employee user (John Doe)
        jdoe_user, created = User.objects.get_or_create(
            username="jdoe",
            defaults={
                "email": "john.doe@meridianhr.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": User.Role.EMPLOYEE,
            },
        )
        if created:
            jdoe_user.set_password("EmployeePass123!")
            jdoe_user.save()

        jdoe_emp, _ = Employee.objects.get_or_create(
            user=jdoe_user,
            defaults={
                "employee_id": "EMP-003",
                "department": dept_eng,
                "designation": "Senior Full Stack Engineer",
                "phone": "+1555019283",
                "date_of_joining": date(2024, 2, 10),
                "salary": 85000.00,
                "status": Employee.Status.ACTIVE,
                "manager": admin_emp,
            },
        )

        # 4. Sample Attendance
        today = timezone.localdate()
        for i in range(5):
            past_date = today - timedelta(days=i)
            Attendance.objects.get_or_create(
                employee=jdoe_emp,
                date=past_date,
                defaults={
                    "check_in": timezone.datetime.strptime("09:00", "%H:%M").time(),
                    "check_out": timezone.datetime.strptime("17:30", "%H:%M").time(),
                    "status": Attendance.Status.PRESENT,
                    "notes": "Regular working day",
                },
            )

        # 5. Sample Leave Requests
        LeaveRequest.objects.get_or_create(
            employee=jdoe_emp,
            leave_type=lt_annual,
            start_date=today + timedelta(days=7),
            end_date=today + timedelta(days=9),
            defaults={
                "reason": "Family trip to the mountains",
                "status": LeaveRequest.Status.PENDING,
            },
        )

        LeaveRequest.objects.get_or_create(
            employee=jdoe_emp,
            leave_type=lt_sick,
            start_date=today - timedelta(days=14),
            end_date=today - timedelta(days=13),
            defaults={
                "reason": "Flu and fever",
                "status": LeaveRequest.Status.APPROVED,
                "reviewed_by": hr_user,
                "reviewed_on": timezone.now() - timedelta(days=14),
                "review_comment": "Approved. Get well soon!",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data seeded successfully!\n"
                "  Admin: admin / AdminPass123!\n"
                "  HR: hr_manager / HrPass123!\n"
                "  Employee: jdoe / EmployeePass123!"
            )
        )
