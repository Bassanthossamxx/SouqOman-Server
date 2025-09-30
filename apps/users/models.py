from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from core.validators import (
    validate_name_ar,
    validate_name_en,
    validate_omani_phone,
)

from .choices import GOVERNORATE_MAP, WILAYAT_MAP


class User(AbstractUser):
    username = None

    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[validate_omani_phone],
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

    USERNAME_FIELD = "phone"  # Phone is the login field
    REQUIRED_FIELDS = [
        "email",
        "full_name_ar",
        "full_name_en",
        "governorate",
        "wilayat",
    ]

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
