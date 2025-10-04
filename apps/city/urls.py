from django.urls import path

from apps.city import views

app_name = "city"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing-page"),
    path("map/", views.CityMapView.as_view(), name="city-map"),
    path("messages/", views.CityMessagesView.as_view(), name="city-messages"),
    path("balance/", views.BalanceView.as_view(), name="balance"),
    path("navbar-values/", views.NavbarValuesView.as_view(), name="navbar-values"),
    # Tiles
    path("tile/<int:pk>/build", views.TileBuildView.as_view(), name="tile-build"),
    path("tile/<int:pk>/demolish", views.TileDemolishView.as_view(), name="tile-demolish"),
    # Savegame
    path("savegame/<int:pk>/values", views.SavegameValueView.as_view(), name="savegame-value"),
    path("savegames/", views.SavegameListView.as_view(), name="savegame-list"),
    path("savegame/create", views.SavegameCreateView.as_view(), name="savegame-create"),
    path("savegame/<int:pk>/load", views.SavegameLoadView.as_view(), name="savegame-load"),
    path("savegame/<int:pk>/delete", views.SavegameDeleteView.as_view(), name="savegame-delete"),
    # Authentication
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
]
