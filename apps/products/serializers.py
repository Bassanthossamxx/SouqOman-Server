from rest_framework import serializers
from django.db import transaction
from .models import Category, SubCategory, Product, ProductImage
from core.choices import WILAYAT_MAP


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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [ "url"]


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        allow_empty=False
    )
    image_urls = ProductImageSerializer(source="images", many=True, read_only=True)
    whatsapp_url = serializers.SerializerMethodField()
    user_full_name_en = serializers.CharField(source="user.full_name_en", read_only=True)
    user_full_name_ar = serializers.CharField(source="user.full_name_ar", read_only=True)
    category_name_en = serializers.CharField(source="category.name_en", read_only=True)
    category_name_ar = serializers.CharField(source="category.name_ar", read_only=True)
    subcategory_name_en = serializers.CharField(source="subcategory.name_en", read_only=True)
    subcategory_name_ar = serializers.CharField(source="subcategory.name_ar", read_only=True)
    # Accept subcategory ID on create/update (optional)
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "user_full_name_en",
            "user_full_name_ar",
            "category",
            "category_name_en",
            "category_name_ar",
            "subcategory",  # include writable field
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
        ]
        read_only_fields = ["id", "user_full_name_en", "user_full_name_ar", "image_urls", "whatsapp_url"]

    def get_whatsapp_url(self, obj):
        return obj.whatsapp_url

    def validate(self, attrs):
        subcategory = attrs.get("subcategory")
        category = attrs.get("category")
        price = attrs.get("price")
        governorate = attrs.get("governorate")
        wilayat = attrs.get("wilayat")

        if subcategory and category and subcategory.category_id != category.id:
            raise serializers.ValidationError({"subcategory": "This subcategory does not belong to the selected category."})
        if not attrs.get("images"):
            raise serializers.ValidationError({"images": "At least one image is required."})
        if not category:
            raise serializers.ValidationError({"category": "Category is required."})
        if price is not None and price < 10.00:
            raise serializers.ValidationError({"price": "Price must be at least 10.00."})
        if governorate and wilayat:
            valid_wilayats = WILAYAT_MAP.get(governorate, {})
            if wilayat not in valid_wilayats.keys():
                raise serializers.ValidationError({"wilayat": f"Wilayat '{wilayat}' is not valid for governorate '{governorate}'."})
        return attrs

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        user = self.context["request"].user

        with transaction.atomic():
            product = Product.objects.create(user=user, **validated_data)
            for img in images[:5]:
                ProductImage.objects.create(product=product, image=img)

        product.refresh_from_db()
        return product
