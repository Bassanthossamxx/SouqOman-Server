from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, SubCategory, Product , AdRequest
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    SubCategorySerializer, ProductSerializer , AdRequestSerializer
)
from core.permissions import IsSuperUserOrReadOnly
from .filters import ProductFilter


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]


class CategoryDetailView(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all().prefetch_related("subcategories")
    serializer_class = CategoryDetailSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = [
        "name_en", "name_ar",
        "category__name_en", "category__name_ar",
        "subcategory__name_en", "subcategory__name_ar"
    ]
    ordering_fields = ["price", "posted_at", "views_count"]
    ordering = ["-posted_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# views.py

class AdRequestCreateView(generics.CreateAPIView):
    queryset = AdRequest.objects.all()
    serializer_class = AdRequestSerializer
    permission_classes = [IsAuthenticated]


class AdVerifyView(generics.UpdateAPIView):
    queryset = AdRequest.objects.all()
    serializer_class = AdRequestSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def patch(self, request, *args, **kwargs):
        ad_request = self.get_object()
        product = ad_request.product

        ad_request.is_approved = True
        ad_request.save()
        product.ad = True
        product.save(update_fields=["ad"])

        return Response({"message": f"Product '{product.name_ar}' marked as Ad."}, status=status.HTTP_200_OK)
