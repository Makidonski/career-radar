from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("me/", views.MeView.as_view(), name="me"),
    path("internal/telegram-link/", views.TelegramLinkView.as_view(), name="telegram-link"),
    path("internal/by-chat-id/<int:chat_id>/", views.InternalUserByChatIdView.as_view(),
         name="by-chat-id"),
]
