from rest_framework import generics
from .models import Category, SubCategory
from .serializers import CategorySerializer, CategoryDetailSerializer, SubCategorySerializer
from core.permissions import IsSuperUserOrReadOnly


# Categories
class CategoryListCreateView(generics.ListCreateAPIView):
    """List & create categories (no subcategories)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]


class CategoryDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve single category (with subcategories)"""
    queryset = Category.objects.all().prefetch_related("subcategories")
    serializer_class = CategoryDetailSerializer
    permission_classes = [IsSuperUserOrReadOnly]


# SubCategories
class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]

