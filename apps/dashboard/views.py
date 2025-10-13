from django.contrib.auth import get_user_model
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.products.filters import ProductFilter
from apps.products.models import AdRequest, Category, Product, SubCategory
from apps.products.serializers import (
    AdRequestSerializer,
    CategorySerializer,
    ProductSerializer,
    SubCategorySerializer,
)
from core.permissions import IsSuperUser

from .serializers import UserDetailSerializer, UserListSerializer

User = get_user_model()


class AdminAllProductsView(generics.ListAPIView):
    """List all products (all statuses) - superuser only"""

    queryset = Product.objects.select_related("user", "category", "subcategory").prefetch_related("images")
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name_en", "name_ar", "category__name_en", "category__name_ar", "subcategory__name_en", "subcategory__name_ar"]
    ordering_fields = ["price", "posted_at", "views_count"]
    ordering = ["-posted_at"]


class AdminApprovePendingProductView(generics.UpdateAPIView):
    """Approve a pending product to make it active"""

    queryset = Product.objects.filter(status=Product.STATUS_PENDING)
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser]

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        product.activate()
        return Response({"message": f"Product '{product.name_ar}' approved and activated."})

    # Some clients use PUT instead of PATCH for action endpoints; accept it and delegate
    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class AdminAdRequestListView(generics.ListAPIView):
    """List all ad requests (superuser only), with optional filter for not approved"""

    serializer_class = AdRequestSerializer
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        queryset = AdRequest.objects.select_related("product", "user")
        is_approved = self.request.query_params.get("is_approved")
        if is_approved == "no":
            queryset = queryset.filter(is_approved=False)
        return queryset


class AdminApproveAdRequestView(generics.UpdateAPIView):
    """Approve AdRequest, set ad start and duration."""

    queryset = AdRequest.objects.all()
    serializer_class = AdRequestSerializer
    permission_classes = [IsSuperUser]

    def patch(self, request, *args, **kwargs):
        ad_request = self.get_object()
        product = ad_request.product

        # Block re-approval attempts
        if ad_request.is_approved:
            return Response(
                {
                    "error": "Ad request is already approved and cannot be modified.",
                    "product": product.pk,
                    "ad_start": ad_request.ad_start,
                    "ad_end": ad_request.ad_end,
                },
                status=status.HTTP_409_CONFLICT,
            )

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

        return Response(
            {
                "message": f"Product '{product.name_ar} - {product.pk}' marked as Ad from {ad_start.date()} to {ad_end.date()}.",
            },
            status=200,
        )


# ========================
# CATEGORY & SUBCATEGORY (ADMIN CREATE)
# ========================


class AdminCategoryCreateView(generics.CreateAPIView):
    """Create a new category - superuser only"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsSuperUser]


class AdminSubCategoryCreateView(generics.CreateAPIView):
    """Create a new subcategory - superuser only"""

    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsSuperUser]


# ========================
# PRODUCT DELETE (ADMIN HARD DELETE)
# ========================


class AdminProductDeleteView(generics.DestroyAPIView):
    """Hard delete a product - superuser only"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSuperUser]


# ========================
# USER MANAGEMENT
# ========================


class AdminUserListView(generics.ListAPIView):
    """List all users - superuser only"""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsSuperUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["phone", "email", "full_name_ar", "full_name_en", "governorate", "wilayat"]
    ordering_fields = ["date_joined", "email", "phone"]
    ordering = ["-date_joined"]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user - superuser only"""

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsSuperUser]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser:
            return Response({"error": "Cannot delete a superuser account"}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class DashboardSuperuserLoginView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        User = get_user_model()
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials or not a superuser."}, status=status.HTTP_401_UNAUTHORIZED)
        if user.check_password(password) and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        return Response({"detail": "Invalid credentials or not a superuser."}, status=status.HTTP_401_UNAUTHORIZED)
