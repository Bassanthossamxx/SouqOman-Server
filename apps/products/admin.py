from django.contrib import admin

from .models import Category, Product, SubCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SubCategory._meta.fields]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]
