from django.urls import path
from .views import (
    # categories
    CategoryListCreateView,
    CategoryDetailView,
    SubCategoryListCreateView,

    # products
    ProductListCreateView,
    ProductDetailView,

    # ads
    AdRequestCreateView,
)

urlpatterns = [
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),

    # Subcategories
    path("subcategories/", SubCategoryListCreateView.as_view(), name="subcategory-list-create"),

    # Products (normal users)
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),

    # Ads
    path("ads/request/", AdRequestCreateView.as_view(), name="ad-request"),
]
