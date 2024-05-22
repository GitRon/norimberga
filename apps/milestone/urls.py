from django.urls import path

from apps.milestone import views

app_name = "milestone"

urlpatterns = [
    path("", views.MilestoneListView.as_view(), name="milestone-list-view"),
]
