from django.urls import path
from .views import MeView, ChangePasswordView, UserListCreateView

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
]
