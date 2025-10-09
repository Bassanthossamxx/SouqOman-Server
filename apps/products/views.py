from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404


from .models import Category, SubCategory, Product, AdRequest
from .serializers import (
    CategorySerializer,
    CategoryDetailSerializer,
    SubCategorySerializer,
    ProductSerializer,
    AdRequestSerializer,
)
from core.permissions import IsSuperUserOrReadOnly , IsOwnerOrSuperUser
from .filters import ProductFilter


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
            message = (
                f"You have reached your free posting limit this month. "
                f"Your product is pending approval. Please contact support at {support}."
            )
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


class AdminAllProductsView(generics.ListAPIView):
    """List all products (all statuses) - superuser only"""
    queryset = Product.objects.select_related("user", "category", "subcategory").prefetch_related("images")
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = [
        "name_en", "name_ar",
        "category__name_en", "category__name_ar",
        "subcategory__name_en", "subcategory__name_ar"
    ]
    ordering_fields = ["price", "posted_at", "views_count"]
    ordering = ["-posted_at"]


class AdminApprovePendingProductView(generics.UpdateAPIView):
    """Approve a pending product to make it active"""
    queryset = Product.objects.filter(status=Product.STATUS_PENDING)
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        product.activate()
        return Response({"message": f"Product '{product.name_ar}' approved and activated."})


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


class AdminAdRequestListView(generics.ListAPIView):
    """List all ad requests (superuser only)"""
    queryset = AdRequest.objects.select_related("product", "user")
    serializer_class = AdRequestSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class AdminApproveAdRequestView(generics.UpdateAPIView):
    """Approve AdRequest, set ad start and duration."""
    queryset = AdRequest.objects.all()
    serializer_class = AdRequestSerializer
    permission_classes = [IsSuperUserOrReadOnly]

    def patch(self, request, *args, **kwargs):
        ad_request = self.get_object()
        product = ad_request.product

        # input expected: {"duration_days": 30} OR {"ad_start": "...", "ad_end": "..."}
        ad_start_str = request.data.get("ad_start")
        ad_end_str = request.data.get("ad_end")
        duration_days = request.data.get("duration_days")

        if ad_start_str:
            ad_start = timezone.datetime.fromisoformat(ad_start_str)
            if timezone.is_naive(ad_start):
                ad_start = timezone.make_aware(ad_start)
        else:
            ad_start = timezone.now()

        if duration_days:
            try:
                duration_days = int(duration_days)
                ad_end = ad_start + timezone.timedelta(days=duration_days)
            except ValueError:
                return Response({"error": "duration_days must be an integer"}, status=400)
        elif ad_end_str:
            ad_end = timezone.datetime.fromisoformat(ad_end_str)
            if timezone.is_naive(ad_end):
                ad_end = timezone.make_aware(ad_end)
        else:
            return Response({"error": "Provide duration_days or ad_end"}, status=400)

        # approve
        ad_request.approve(request.user, ad_start, ad_end)
        # make sure product is active
        if product.status != Product.STATUS_ACTIVE:
            product.activate()

        return Response({
            "message": f"Product '{product.name_ar}' marked as Ad from {ad_start.date()} to {ad_end.date()}."
        }, status=200)
