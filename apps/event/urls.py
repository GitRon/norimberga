from django.urls import path

from apps.event import views

app_name = "event"

urlpatterns = [
    path("notifications/", views.NotificationBoardView.as_view(), name="notification-board"),
    path(
        "notifications/<int:pk>/acknowledge/",
        views.NotificationAcknowledgeView.as_view(),
        name="notification-acknowledge",
    ),
]
