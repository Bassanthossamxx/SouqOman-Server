from rest_framework import serializers
from .models import Category, SubCategory , Product
from core.utils import upload_to_imagekit

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["id", "name_en", "name_ar", "category"]


class CategorySerializer(serializers.ModelSerializer):
    """Used for list & create (no subcategories)"""
    class Meta:
        model = Category
        fields = ["id", "name_en", "name_ar"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Used for retrieve (with subcategories)"""
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name_en", "name_ar", "subcategories"]

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    whatsapp_url = serializers.SerializerMethodField()
    user_full_name_en = serializers.CharField(source="user.full_name_en", read_only=True)
    user_full_name_ar = serializers.CharField(source="user.full_name_ar", read_only=True)
    category_name_en = serializers.CharField(source="category.name_en", read_only=True)
    category_name_ar = serializers.CharField(source="category.name_ar", read_only=True)
    subcategory_name_en = serializers.CharField(source="subcategory.name_en", read_only=True)
    subcategory_name_ar = serializers.CharField(source="subcategory.name_ar", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "user_full_name_en",
            "user_full_name_ar",
            "category_name_en",
            "category_name_ar",
            "subcategory_name_en",
            "subcategory_name_ar",
            "name_en",
            "name_ar",
            "governorate",
            "wilayat",
            "image_urls",
            "price",
            "description",
            "contact_phone",
            "whatsapp_url",
            "images",
        ]
        read_only_fields = [
            "id",
            "user_full_name_en",
            "user_full_name_ar",
            "image_urls",
            "whatsapp_url",
        ]

    def get_whatsapp_url(self, obj):
        return obj.whatsapp_url

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        user = self.context["request"].user

        uploaded_urls = []
        for img in images[:5]:
            url = upload_to_imagekit(img)
            uploaded_urls.append(url)

        product = Product.objects.create(
            user=user,
            image_urls=uploaded_urls,
            **validated_data
        )
        return product
