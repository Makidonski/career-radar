from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import InternalServicePermission
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    TelegramLinkSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/ - create an account and return an auth token."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/users/login/ - exchange username/password for an auth token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/me/ - the authenticated user's own profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class TelegramLinkView(APIView):
    """POST /api/users/internal/telegram-link/

    Called by the Telegram bot (with the internal shared secret) once a user
    starts a chat and shares their identity, so subsequent /digest, /stats,
    /alerts commands can be tied back to a CareerRadar account.
    """

    permission_classes = [InternalServicePermission]

    def post(self, request):
        serializer = TelegramLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data["username"])
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.telegram_chat_id = data["telegram_chat_id"]
        user.telegram_username = data.get("telegram_username", "")
        user.save(update_fields=["telegram_chat_id", "telegram_username"])
        return Response(UserSerializer(user).data)


class InternalUserByChatIdView(APIView):
    """GET /api/users/internal/by-chat-id/<chat_id>/

    Used by the bot to resolve which CareerRadar profile a Telegram chat
    belongs to, so it can fetch that user's filters/skills for /digest.
    """

    permission_classes = [InternalServicePermission]

    def get(self, request, chat_id):
        try:
            user = User.objects.get(telegram_chat_id=chat_id)
        except User.DoesNotExist:
            return Response({"detail": "Not linked"}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)
