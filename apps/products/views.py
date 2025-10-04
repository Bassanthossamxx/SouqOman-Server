from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category
from .serializers import CategorySerializer
from core.permissions import IsSuperUserOrReadOnly

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().prefetch_related("subcategories")
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]


class CategoryDetailView(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all().prefetch_related("subcategories")
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]
