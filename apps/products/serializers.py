from rest_framework import serializers
from .models import Category, SubCategory


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
