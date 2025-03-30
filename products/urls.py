from django.urls import path
from .views import (
    ProductView,
    ProductDetailView,
    ProductSearchView,
    ProductMetricsView,
    ProductSortView,
    CategoryView,
    CategoryDetailView,
)

urlpatterns = [
    # Product endpoints
    path("products/", ProductView.as_view(), name="product-list"),
    path(
        "products/<str:product_id>/", ProductDetailView.as_view(), name="product-detail"
    ),
    path("products/search/", ProductSearchView.as_view(), name="product-search"),
    path("products/metrics/", ProductMetricsView.as_view(), name="product-metrics"),
    path("products/sort/", ProductSortView.as_view(), name="product-sort"),
    # Category endpoints
    path("categories/", CategoryView.as_view(), name="category-list"),
    path(
        "categories/<str:category_id>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
]
