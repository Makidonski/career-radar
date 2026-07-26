from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("vacancies", views.VacancyViewSet, basename="vacancy")
router.register("filters", views.SearchFilterViewSet, basename="search-filter")
router.register("history", views.ViewHistoryViewSet, basename="view-history")
router.register("alerts", views.AlertViewSet, basename="alert")

urlpatterns = [
    path("internal/telegram-alerts/", views.InternalTelegramAlertsView.as_view(),
         name="internal-telegram-alerts"),
    path("internal/telegram-digest/", views.InternalTelegramDigestView.as_view(),
         name="internal-telegram-digest"),
    path("", include(router.urls)),
]
