from django.conf import settings
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsOwnerOrSuperUser, IsSuperUserOrReadOnly

from .filters import ProductFilter
from .models import AdRequest, Category, Product, SubCategory
from .serializers import (
    AdRequestSerializer,
    CategoryDetailSerializer,
    CategorySerializer,
    ProductSerializer,
    SubCategorySerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all().prefetch_related("subcategories")
    serializer_class = CategoryDetailSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsSuperUserOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name_en", "name_ar", "category__name_en", "category__name_ar", "subcategory__name_en", "subcategory__name_ar"]
    ordering_fields = ["price", "posted_at", "views_count"]
    ordering = ["-posted_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        now = timezone.now()

        # Auto-expire ads whose end date has passed
        Product.objects.filter(ad=True, ad_end__lt=now).update(ad=False, ad_start=None, ad_end=None)

        qs = Product.objects.select_related("user", "category", "subcategory").prefetch_related("images")
        user = self.request.user

        if user.is_authenticated and user.is_superuser:
            # superuser sees all statuses
            return qs

        # normal or anonymous users see only active products
        return qs.filter(status=Product.STATUS_ACTIVE)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        data = ProductSerializer(product, context={"request": request}).data

        #  Check status and respond accordingly
        if product.status == Product.STATUS_PENDING:
            support = getattr(settings, "SUPPORT_PHONE", "support")
            message = f"You have reached your free posting limit this month. Your product is pending approval. Please contact support at {support}."
            return Response({**data, "message": message}, status=status.HTTP_201_CREATED)

        return Response(data, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("user", "category", "subcategory").prefetch_related("images")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOrSuperUser()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # increase views
        instance.views_count += 1
        instance.save(update_fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_superuser:
            # hard delete
            instance.delete()
        else:
            # soft delete
            instance.soft_delete()


# -------------------------------
#  AD REQUEST VIEWS
# -------------------------------


class AdRequestCreateView(generics.CreateAPIView):
    queryset = AdRequest.objects.all()
    serializer_class = AdRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        ad_request = serializer.save()
        msg = "Ad request successful. Our team will contact you soon via phone or WhatsApp."
        return Response({**AdRequestSerializer(ad_request).data, "message": msg}, status=status.HTTP_201_CREATED)
