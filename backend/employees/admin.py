from django.contrib import admin
from .models import Employee, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "designation", "status", "date_of_joining")
    list_filter = ("department", "status")
    search_fields = ("employee_id", "user__first_name", "user__last_name", "user__email")
