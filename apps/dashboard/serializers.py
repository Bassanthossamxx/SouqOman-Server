from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users in dashboard - superuser only"""

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "full_name_ar",
            "full_name_en",
            "governorate",
            "wilayat",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "extra_monthly_posts",
        ]
        read_only_fields = ["id", "date_joined"]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for dashboard"""

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "full_name_ar",
            "full_name_en",
            "governorate",
            "wilayat",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "extra_monthly_posts",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
