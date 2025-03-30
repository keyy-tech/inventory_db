from django.urls import path
from .views import InventoryTransactionView, InventoryTransactionDetailView

urlpatterns = [
    path("transactions/", InventoryTransactionView.as_view(), name="transaction_view"),
    path(
        "transactions/<str:transaction_id>/",
        InventoryTransactionDetailView.as_view(),
        name="transaction_detail_view",
    ),
]
