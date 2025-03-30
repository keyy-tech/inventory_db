from django.urls import path
from .views import LocationView, LocationDetailView

urlpatterns = [
    path("locations/", LocationView.as_view(), name="location_view"),
    path(
        "locations/<str:location_id>/",
        LocationDetailView.as_view(),
        name="location_detail_view",
    ),
]
