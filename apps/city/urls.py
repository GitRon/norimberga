from django.urls import path

from apps.city import views

app_name = "city"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing-page"),
    path("map/", views.CityMapView.as_view(), name="city-map"),
    # Tiles
    path("tile/<int:pk>/build", views.TileBuildView.as_view(), name="tile-build"),
    # Savegame
    path("savegame/<int:pk>/coins", views.CoinUpdateView.as_view(), name="savegame-coins"),
]
