from rest_framework.routers import DefaultRouter
from .views import LeaveRequestViewSet, LeaveTypeViewSet

router = DefaultRouter()
router.register("types", LeaveTypeViewSet, basename="leave-type")
router.register("", LeaveRequestViewSet, basename="leave-request")

urlpatterns = router.urls
