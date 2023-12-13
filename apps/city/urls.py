from django.urls import path

from apps.city import views

app_name = "city"

urlpatterns = [
    path("map/", views.CityMapView.as_view(), name="city-map"),
]
