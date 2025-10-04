from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    SubCategoryListCreateView,
)

urlpatterns = [
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),

    # SubCategories
    path("subcategories/", SubCategoryListCreateView.as_view(), name="subcategory-list-create"),
]
