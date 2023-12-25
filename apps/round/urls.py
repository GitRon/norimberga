from django.urls import path

from apps.round import views

app_name = "round"

urlpatterns = [
    path("finish/", views.RoundView.as_view(), name="finish"),
]
