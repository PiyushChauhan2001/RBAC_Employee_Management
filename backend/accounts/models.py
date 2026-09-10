from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role that drives permissions across the system."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        HR = "HR", "HR Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EMPLOYEE)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_admin_or_hr(self):
        return self.role in (self.Role.ADMIN, self.Role.HR)
