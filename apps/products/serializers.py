# serializers.py
from calendar import monthrange
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Category, SubCategory, Product, ProductImage, AdRequest

# --- simple category/subcategory serializers ---
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["id", "name_en", "name_ar", "category"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name_en", "name_ar"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ["id", "name_en", "name_ar", "subcategories"]


# --- images ---
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["url"]


# --- product serializer ---
class ProductSerializer(serializers.ModelSerializer):
    # client uploads images as files (list)
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        allow_empty=False
    )
    # read-only array of image urls
    image_urls = ProductImageSerializer(source="images", many=True, read_only=True)

    whatsapp_url = serializers.SerializerMethodField()
    user_full_name_en = serializers.CharField(source="user.full_name_en", read_only=True)
    user_full_name_ar = serializers.CharField(source="user.full_name_ar", read_only=True)
    category_name_en = serializers.CharField(source="category.name_en", read_only=True)
    category_name_ar = serializers.CharField(source="category.name_ar", read_only=True)
    subcategory_name_en = serializers.CharField(source="subcategory.name_en", read_only=True)
    subcategory_name_ar = serializers.CharField(source="subcategory.name_ar", read_only=True)

    # important: user shouldn't set these directly
    read_only_fields = ["id", "user_full_name_en", "user_full_name_ar", "image_urls", "whatsapp_url",
                        "status", "ad", "posted_at"]

    class Meta:
        model = Product
        fields = [
            "id",
            "user_full_name_en",
            "user_full_name_ar",
            "category",
            "category_name_en",
            "category_name_ar",
            "subcategory",
            "subcategory_name_en",
            "subcategory_name_ar",
            "name_en",
            "name_ar",
            "governorate",
            "wilayat",
            "price",
            "description",
            "contact_phone",
            "whatsapp_url",
            "images",
            "image_urls",
            "status",
            "ad",
            "posted_at",
        ]
        extra_kwargs = {
            "status": {"read_only": True},
            "ad": {"read_only": True},
            "posted_at": {"read_only": True},
        }

    def get_whatsapp_url(self, obj):
        return obj.whatsapp_url

    def validate(self, attrs):
        # check subcategory belongs to category if both provided
        subcategory = attrs.get("subcategory")
        category = attrs.get("category")
        price = attrs.get("price")
        governorate = attrs.get("governorate")
        wilayat = attrs.get("wilayat")

        if subcategory and category and subcategory.category_id != category.id:
            raise serializers.ValidationError({"subcategory": "This subcategory does not belong to the selected category."})

        if price is not None and price < 10.00:
            raise serializers.ValidationError({"price": "Price must be at least 10.00."})

        if governorate and wilayat:
            valid_wilayats = WILAYAT_MAP.get(governorate, {})
            if wilayat not in valid_wilayats.keys():
                raise serializers.ValidationError({"wilayat": f"Wilayat '{wilayat}' is not valid for governorate '{governorate}'."})

        # images validated by field-level; ensure not empty
        images = attrs.get("images") or []
        if not images:
            raise serializers.ValidationError({"images": "At least one image is required."})
        if len(images) > 5:
            raise serializers.ValidationError({"images": "At most 5 images allowed."})

        return attrs

    def _current_month_start(self):
        now = timezone.now()
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _user_monthly_count(self, user):
        start = self._current_month_start()
        # count only active & pending posts in current month (inactive = user deleted -> should not count)
        return Product.objects.filter(
            user=user,
            posted_at__gte=start,
            status__in=[Product.STATUS_ACTIVE, Product.STATUS_PENDING]
        ).count()

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        request = self.context.get("request")
        if request is None or not request.user or request.user.is_anonymous:
            raise serializers.ValidationError("Authentication required to create product.")
        user = request.user

        # compute effective monthly quota
        base_free = getattr(settings, "FREE_PRODUCTS_PER_MONTH", 4)
        extra = getattr(user, "extra_monthly_posts", 0) or 0
        effective_quota = base_free + extra

        current_count = self._user_monthly_count(user)

        status = Product.STATUS_ACTIVE if current_count < effective_quota else Product.STATUS_PENDING

        with transaction.atomic():
            product = Product.objects.create(user=user, status=status, **validated_data)
            # create images (ProductImage.save uploads to Cloudinary)
            for img in images[:5]:
                ProductImage.objects.create(product=product, image=img)

        product.refresh_from_db()
        return product


# --- ad request serializer ---
class AdRequestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    ad_start = serializers.DateTimeField(read_only=True)
    ad_end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AdRequest
        fields = ["id", "product", "is_approved", "ad_start", "ad_end", "created_at"]
        read_only_fields = ["id", "is_approved", "ad_start", "ad_end", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product")

        if product.user_id != user.id:
            raise serializers.ValidationError("You can only request an ad for your own product.")

        if product.status == Product.STATUS_INACTIVE:
            raise serializers.ValidationError("Cannot request ad for an inactive product.")

        if AdRequest.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("You already requested an ad for this product.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product"]
        # create request
        return AdRequest.objects.create(user=user, product=product)
