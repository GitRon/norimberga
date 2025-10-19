from django.urls import path

from apps.edict import views

app_name = "edict"

urlpatterns = [
    path("", views.EdictListView.as_view(), name="edict-list-view"),
    path("<int:pk>/activate/", views.EdictActivateView.as_view(), name="edict-activate"),
]
