from django.urls import path
from .views import (
    # Product management
    AdminAllProductsView,
    AdminApprovePendingProductView,

    # Ad request management
    AdminAdRequestListView,
    AdminApproveAdRequestView,

    # User management
    AdminUserListView,
    AdminUserDetailView,
)

urlpatterns = [
    # Product management
    path("products/", AdminAllProductsView.as_view(), name="dashboard-all-products"),
    path("products/<int:pk>/approve/", AdminApprovePendingProductView.as_view(), name="dashboard-approve-pending"),

    # Ad request management
    path("ads/", AdminAdRequestListView.as_view(), name="dashboard-ad-list"),
    path("ads/<int:pk>/approve/", AdminApproveAdRequestView.as_view(), name="dashboard-ad-approve"),

    # User management
    path("users/", AdminUserListView.as_view(), name="dashboard-user-list"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="dashboard-user-detail"),
]

