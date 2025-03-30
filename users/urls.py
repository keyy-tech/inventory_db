from django.urls import path
from .views import UserView, UserDetailView

urlpatterns = [
    path("users/", UserView.as_view(), name="user_view"),
    path("users/<str:user_id>/", UserDetailView.as_view(), name="user_detail_view"),
]
