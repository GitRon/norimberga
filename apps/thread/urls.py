from django.urls import path

from apps.thread import views

app_name = "thread"

urlpatterns = [
    path("", views.ThreadsView.as_view(), name="threads"),
    path("defense/", views.DefenseTabView.as_view(), name="defense-tab"),
    path("prestige/", views.PrestigeTabView.as_view(), name="prestige-tab"),
    path("active/", views.ThreadsTabView.as_view(), name="threads-tab"),
]
