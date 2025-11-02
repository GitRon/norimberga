from django.urls import path

from apps.event import views

app_name = "event"

urlpatterns = [
    path("pending/", views.PendingEventsView.as_view(), name="pending"),
    path("choice/<int:pk>/", views.EventChoiceSelectView.as_view(), name="select-choice"),
]
