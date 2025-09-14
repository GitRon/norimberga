from django.urls import path

from apps.city import views

app_name = "city"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing-page"),
    path("map/", views.CityMapView.as_view(), name="city-map"),
    path("messages/", views.CityMessagesView.as_view(), name="city-messages"),
    # Tiles
    path("tile/<int:pk>/build", views.TileBuildView.as_view(), name="tile-build"),
    path("tile/<int:pk>/demolish", views.TileDemolishView.as_view(), name="tile-demolish"),
    # Savegame
    path("savegame/<int:pk>/values", views.SavegameValueView.as_view(), name="savegame-value"),
]
