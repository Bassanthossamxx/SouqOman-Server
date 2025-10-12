from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from datetime import timedelta

from core.validators import (
    validate_name_ar,
    validate_name_en,
    validate_omani_phone,
)

from core.choices import GOVERNORATE_MAP, WILAYAT_MAP


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, email, full_name_ar, full_name_en, governorate, wilayat, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        if not full_name_ar:
            raise ValueError('The Arabic full name must be set')
        if not full_name_en:
            raise ValueError('The English full name must be set')
        if not governorate:
            raise ValueError('The Governorate must be set')
        if not wilayat:
            raise ValueError('The Wilayat must be set')
        email = self.normalize_email(email)
        user = self.model(
            phone=phone,
            email=email,
            full_name_ar=full_name_ar,
            full_name_en=full_name_en,
            governorate=governorate,
            wilayat=wilayat,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email, full_name_ar, full_name_en, governorate, wilayat, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone, email, full_name_ar, full_name_en, governorate, wilayat, password, **extra_fields)


class User(AbstractUser):
    username = None

    phone = models.CharField(
        max_length=15,
        unique=True,
        # validators=[validate_omani_phone],
        blank=False,
        null=False,
    )
    email = models.EmailField(unique=True)

    full_name_ar = models.CharField(
        max_length=100,
        validators=[validate_name_ar],
    )
    full_name_en = models.CharField(
        max_length=100,
        validators=[validate_name_en],
    )

    governorate = models.CharField(
        max_length=50,
        choices=[(gov, gov) for gov in GOVERNORATE_MAP.keys()],
    )
    wilayat = models.CharField(max_length=50)
    extra_monthly_posts = models.IntegerField(default=0, help_text="extra free posts added by admin for current month")

    USERNAME_FIELD = "phone"  # Phone is the login field
    REQUIRED_FIELDS = [
        "email",
        "full_name_ar",
        "full_name_en",
        "governorate",
        "wilayat",
    ]

    objects = UserManager()  # Set custom manager

    def __str__(self):
        return f"{self.full_name_en} / {self.full_name_ar} ({self.phone})"

    def clean(self):
        """
        Ensure wilayat belongs to the selected governorate.
        Validates both at model level (for admin & saves)
        """
        if self.governorate:
            valid_wilayats = WILAYAT_MAP.get(self.governorate, {})
            if self.wilayat not in valid_wilayats.keys():
                raise ValidationError({"wilayat": f"{self.wilayat} is not valid for {self.governorate}"})


class PhoneVerification(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    transaction_id = models.CharField(max_length=100)
    request_id = models.CharField(max_length=100, blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Verified" if self.verified else "Pending"
        return f"{self.phone} - {status}"

    def can_resend(self):
        """
        Allow resend only if 60 seconds have passed since last update.
        """
        return self.updated_at < timezone.now() - timedelta(seconds=60)
