from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.permissions import InternalServicePermission

from .filters import VacancyFilter
from .models import Alert, SearchFilter, Vacancy, ViewHistory
from .serializers import (
    AlertSerializer,
    SearchFilterSerializer,
    VacancySerializer,
    ViewHistorySerializer,
)


class VacancyViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only browse/search API for parsed vacancies, used by the
    dashboard frontend and the Telegram bot's /digest command."""

    queryset = Vacancy.objects.all().prefetch_related("skills").order_by("-published_at")
    serializer_class = VacancySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = VacancyFilter


class SearchFilterViewSet(viewsets.ModelViewSet):
    serializer_class = SearchFilterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SearchFilter.objects.filter(user=self.request.user).order_by("-created_at")


class ViewHistoryViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "head"]
    serializer_class = ViewHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ViewHistory.objects.filter(user=self.request.user).order_by("-viewed_at")


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        # `user` is deliberately excluded from AlertSerializer's writable
        # fields, so it must be injected here from the authenticated
        # request rather than trusted from client input.
        serializer.save(user=self.request.user)


class InternalTelegramAlertsView(APIView):
    """GET/POST /api/vacancies/internal/telegram-alerts/?chat_id=...

    Lets the Telegram bot list or create Alerts for a user identified only
    by their telegram_chat_id, without needing that user's DRF auth token.
    Trusted exclusively via the internal shared secret.
    """

    permission_classes = [InternalServicePermission]

    def get(self, request):
        chat_id = request.query_params.get("chat_id")
        user = get_object_or_404(User, telegram_chat_id=chat_id)
        alerts = Alert.objects.filter(user=user).order_by("-created_at")
        return Response(AlertSerializer(alerts, many=True).data)

    def post(self, request):
        chat_id = request.data.get("chat_id")
        user = get_object_or_404(User, telegram_chat_id=chat_id)
        serializer = AlertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InternalTelegramDigestView(APIView):
    """GET /api/vacancies/internal/telegram-digest/?chat_id=...&limit=5

    Returns the most recent vacancies matching the user's profile
    (desired_position / city / min_salary), used by the bot's /digest command.
    """

    permission_classes = [InternalServicePermission]

    def get(self, request):
        chat_id = request.query_params.get("chat_id")
        limit = int(request.query_params.get("limit", 5))
        user = get_object_or_404(User, telegram_chat_id=chat_id)

        qs = Vacancy.objects.all().prefetch_related("skills")
        if user.desired_position:
            qs = qs.filter(title__icontains=user.desired_position)
        if user.city:
            qs = qs.filter(city__iexact=user.city)
        if user.min_salary:
            qs = qs.filter(salary_from__gte=user.min_salary)

        vacancies = qs.order_by("-published_at")[:limit]
        return Response(VacancySerializer(vacancies, many=True).data)
