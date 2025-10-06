from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from core.choices import GOVERNORATE_MAP, WILAYAT_MAP
from core.validators import validate_omani_phone, validate_name_ar, validate_name_en

class Category(models.Model):
    name_en = models.CharField(max_length=255, unique=True, validators=[validate_name_en])
    name_ar = models.CharField(max_length=255, unique=True, validators=[validate_name_ar])

    def __str__(self):
        return self.name_ar


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name_en = models.CharField(max_length=255, validators=[validate_name_en])
    name_ar = models.CharField(max_length=255, validators=[validate_name_ar])

    class Meta:
        unique_together = [
            ("category", "name_ar"),
            ("category", "name_en"),
        ]

    def __str__(self):
        return f"{self.name_ar} ({self.category.name_ar})"


class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey("SubCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    name_en = models.CharField(max_length=255, blank=True, null=True, validators=[validate_name_en])
    name_ar = models.CharField(max_length=255,blank=False, null=False, validators=[validate_name_ar])  # required

    governorate = models.CharField(
        max_length=50,
        choices=[(gov, gov) for gov in GOVERNORATE_MAP.keys()]
    )
    wilayat = models.CharField(max_length=50)

    image_urls = models.JSONField(default=list, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    posted_at = models.DateTimeField(default=timezone.now)
    views_count = models.PositiveIntegerField(default=0)
    contact_phone = models.CharField(max_length=20, validators=[validate_omani_phone]) # will check is new one or use user phone

    def clean(self):
        """Ensure wilayat belongs to the selected governorate."""
        if self.governorate:
            valid_wilayats = WILAYAT_MAP.get(self.governorate, {})
            if self.wilayat not in valid_wilayats.keys():
                raise ValidationError({"wilayat": f"{self.wilayat} is not valid for {self.governorate}"})

    def save(self, *args, **kwargs):
        # Limit to 5 images
        if self.image_urls and len(self.image_urls) > 5:
            self.image_urls = self.image_urls[:5]
        super().save(*args, **kwargs)

    @property
    def whatsapp_url(self):
        """Generate WhatsApp link from contact phone."""
        if not self.contact_phone:
            return None
        phone_number = self.contact_phone.replace("+", "").replace(" ", "")
        return f"https://wa.me/{phone_number}"

    def __str__(self):
        return self.name_ar
