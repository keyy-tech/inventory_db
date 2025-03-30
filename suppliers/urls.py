from django.urls import path
from .views import SupplierView, SupplierDetailView

urlpatterns = [
    path("suppliers/", SupplierView.as_view(), name="supplier_view"),
    path(
        "suppliers/<str:supplier_id>/",
        SupplierDetailView.as_view(),
        name="supplier_detail_view",
    ),
]
