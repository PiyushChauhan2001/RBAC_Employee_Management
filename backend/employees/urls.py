from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("", EmployeeViewSet, basename="employee")

urlpatterns = router.urls
