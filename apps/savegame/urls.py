from django.urls import path

from apps.savegame import views

app_name = "savegame"

urlpatterns = [
    path("balance/", views.BalanceView.as_view(), name="balance"),
    path("savegame/<int:pk>/values", views.SavegameValueView.as_view(), name="savegame-value"),
    path("savegames/", views.SavegameListView.as_view(), name="savegame-list"),
    path("savegame/create", views.SavegameCreateView.as_view(), name="savegame-create"),
    path("savegame/<int:pk>/load", views.SavegameLoadView.as_view(), name="savegame-load"),
    path("savegame/<int:pk>/delete", views.SavegameDeleteView.as_view(), name="savegame-delete"),
]
