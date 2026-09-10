from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    CreateUserSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdminOrHR

User = get_user_model()


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Login endpoint. Rate-limited to blunt credential-stuffing / brute force attempts."""

    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = "login"


class LogoutView(APIView):
    """Blacklists the supplied refresh token so it can no longer mint new access tokens."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid or missing refresh token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """The logged-in user's own profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."})


class UserListCreateView(generics.ListCreateAPIView):
    """Admin/HR provision logins for new staff. Regular employees cannot list all users."""

    queryset = User.objects.all().order_by("username")
    permission_classes = [IsAdminOrHR]

    def get_serializer_class(self):
        return CreateUserSerializer if self.request.method == "POST" else UserSerializer
