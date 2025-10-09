from django.urls import path
from .views import (
    # categories
    CategoryListCreateView,
    CategoryDetailView,
    SubCategoryListCreateView,

    # products
    ProductListCreateView,
    ProductDetailView,
    AdminAllProductsView,
    AdminApprovePendingProductView,

    # ads
    AdRequestCreateView,
    AdminAdRequestListView,
    AdminApproveAdRequestView,
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

    # Admin product management
    path("admin/products/", AdminAllProductsView.as_view(), name="admin-all-products"),
    path("admin/products/<int:pk>/approve/", AdminApprovePendingProductView.as_view(), name="admin-approve-pending"),

    # Ads
    path("ads/request/", AdRequestCreateView.as_view(), name="ad-request"),
    path("admin/ads/", AdminAdRequestListView.as_view(), name="admin-ad-list"),
    path("admin/ads/<int:pk>/approve/", AdminApproveAdRequestView.as_view(), name="admin-ad-approve"),
]
