# filepath: d:\freelance work\SouqOman-Server\apps\products\filters.py
from django.db.models import Q
import django_filters

from .models import Product
from core.choices import GOVERNORATE_MAP, WILAYAT_MAP


class ProductFilter(django_filters.FilterSet):
    """
    Supported query params:
    - name: string, matches Product name in EN or AR (icontains)
    - min_price: number, price >= min_price
    - max_price: number, price <= max_price
    - category: string, matches Category name in EN or AR (icontains)
    - subcategory: string, matches SubCategory name in EN or AR (icontains)
    - wilayat: string, accepts EN or AR (partial EN icontains or AR exact/partial to its EN key)
    - governorate: string, accepts EN or AR (partial EN icontains or AR exact/partial to its EN key)
    """

    name = django_filters.CharFilter(method="filter_name")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(method="filter_category")
    subcategory = django_filters.CharFilter(method="filter_subcategory")
    wilayat = django_filters.CharFilter(method="filter_wilayat")
    governorate = django_filters.CharFilter(method="filter_governorate")

    class Meta:
        model = Product
        fields = [
            "name",
            "wilayat",
            "governorate",
            "min_price",
            "max_price",
            "category",
            "subcategory",
        ]

    def filter_name(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(Q(name_en__icontains=value) | Q(name_ar__icontains=value))

    def filter_category(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(category__name_en__icontains=value) | Q(category__name_ar__icontains=value)
        )

    def filter_subcategory(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(subcategory__name_en__icontains=value) | Q(subcategory__name_ar__icontains=value)
        )

    def _match_governorates(self, term: str):
        term_lower = term.lower()
        matches = set()
        for en, ar in GOVERNORATE_MAP.items():
            if term_lower in en.lower() or term_lower in ar.lower():
                matches.add(en)
        return list(matches)

    def _match_wilayats(self, term: str):
        term_lower = term.lower()
        matches = set()
        for gov_en, wil_map in WILAYAT_MAP.items():
            for wil_en, wil_ar in wil_map.items():
                if term_lower in wil_en.lower() or term_lower in wil_ar.lower():
                    matches.add(wil_en)
        return list(matches)

    def filter_governorate(self, queryset, name, value):
        if not value:
            return queryset
        candidates = self._match_governorates(value)
        if not candidates:
            return queryset.none()
        return queryset.filter(governorate__in=candidates)

    def filter_wilayat(self, queryset, name, value):
        if not value:
            return queryset
        candidates = self._match_wilayats(value)
        if not candidates:
            return queryset.none()
        return queryset.filter(wilayat__in=candidates)
