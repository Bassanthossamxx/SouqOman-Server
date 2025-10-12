from django.urls import path
from .views import (
    # Product management
    AdminAllProductsView,
    AdminApprovePendingProductView,
    AdminProductDeleteView,

    # Category/Subcategory management
    AdminCategoryCreateView,
    AdminSubCategoryCreateView,

    # Ad request management
    AdminAdRequestListView,
    AdminApproveAdRequestView,

    # User management
    AdminUserListView,
    AdminUserDetailView,

    # Superuser login
    DashboardSuperuserLoginView,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # Product management
    path("products/", AdminAllProductsView.as_view(), name="dashboard-all-products"),
    path("products/<int:pk>/approve/", AdminApprovePendingProductView.as_view(), name="dashboard-approve-pending"),
    path("products/<int:pk>/", AdminProductDeleteView.as_view(), name="dashboard-product-delete"),  # DELETE only

    # Category/Subcategory management
    path("categories/", AdminCategoryCreateView.as_view(), name="dashboard-category-create"),  # POST only
    path("subcategories/", AdminSubCategoryCreateView.as_view(), name="dashboard-subcategory-create"),  # POST only

    # Ad request management
    path("ads/", AdminAdRequestListView.as_view(), name="dashboard-ad-list"),
    path("ads/<int:pk>/approve/", AdminApproveAdRequestView.as_view(), name="dashboard-ad-approve"),

    # User management
    path("users/", AdminUserListView.as_view(), name="dashboard-user-list"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="dashboard-user-detail"),

    # Superuser login
    path("/login/", DashboardSuperuserLoginView.as_view(), name="dashboard-superuser-login"),

    # JWT token management
    path("token/refresh/", TokenRefreshView.as_view(), name="dashboard-token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="dashboard-token-verify"),
]
