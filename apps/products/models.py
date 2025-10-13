import cloudinary.uploader
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.choices import GOVERNORATE_MAP, WILAYAT_MAP
from core.validators import validate_name_ar, validate_name_en, validate_omani_phone

ALL_WILAYAT_CHOICES = [(wil, wil) for _gov, wmap in WILAYAT_MAP.items() for wil in wmap.keys()]


class Category(models.Model):
    name_en = models.CharField(max_length=255, unique=True, validators=[validate_name_en])
    name_ar = models.CharField(max_length=255, unique=True, validators=[validate_name_ar])
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    image_url = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        # Upload to Cloudinary if image file is present and no URL yet
        if self.image and not self.image_url:
            upload_result = cloudinary.uploader.upload(self.image)
            self.image_url = upload_result.get("secure_url")
            # Remove local file to avoid storing media on disk
            try:
                self.image.delete(save=False)
            except Exception:
                pass
            self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_ar


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name_en = models.CharField(max_length=255, validators=[validate_name_en])
    name_ar = models.CharField(max_length=255, validators=[validate_name_ar])
    image = models.ImageField(upload_to="subcategories/", blank=True, null=True)
    image_url = models.URLField(blank=True)

    class Meta:
        unique_together = [("category", "name_ar"), ("category", "name_en")]

    def save(self, *args, **kwargs):
        # Upload to Cloudinary if image file is present and no URL yet
        if self.image and not self.image_url:
            upload_result = cloudinary.uploader.upload(self.image)
            self.image_url = upload_result.get("secure_url")
            # Remove local file to avoid storing media on disk
            try:
                self.image.delete(save=False)
            except Exception:
                pass
            self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_ar} ({self.category.name_ar})"


class Product(models.Model):
    # Status choices
    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),  # user "deleted" products -> inactive
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="products")
    subcategory = models.ForeignKey("SubCategory", on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    name_en = models.CharField(max_length=255, blank=True, null=True, validators=[validate_name_en])
    name_ar = models.CharField(max_length=255, blank=False, null=False, validators=[validate_name_ar])

    governorate = models.CharField(max_length=50, choices=[(gov, gov) for gov in GOVERNORATE_MAP.keys()])
    wilayat = models.CharField(max_length=50, choices=ALL_WILAYAT_CHOICES)

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(10.00)])
    description = models.TextField()
    posted_at = models.DateTimeField(default=timezone.now)
    views_count = models.PositiveIntegerField(default=0)
    contact_phone = models.CharField(max_length=20, validators=[validate_omani_phone])

    # status replaces boolean flags for overall lifecycle
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)

    # Ad fields
    ad = models.BooleanField(default=False, help_text="True if product is a verified paid ad")
    ad_start = models.DateTimeField(null=True, blank=True)
    ad_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-posted_at"]

    def clean(self):
        if self.governorate:
            valid_wilayats = WILAYAT_MAP.get(self.governorate, {})
            if self.wilayat not in valid_wilayats.keys():
                raise ValidationError({"wilayat": f"{self.wilayat} is not valid for {self.governorate}"})

    @property
    def whatsapp_url(self):
        if not self.contact_phone:
            return None
        phone_number = self.contact_phone.replace("+", "").replace(" ", "")
        return f"https://wa.me/{phone_number}"

    # convenience boolean properties
    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def is_inactive(self):
        return self.status == self.STATUS_INACTIVE

    def soft_delete(self):
        """User-level delete -> mark inactive (not visible to normal users)."""
        self.status = self.STATUS_INACTIVE
        self.save(update_fields=["status"])

    def mark_pending(self):
        """Mark product as pending (e.g., user exceeded free quota)."""
        self.status = self.STATUS_PENDING
        self.save(update_fields=["status"])

    def activate(self):
        """Make product visible (used by admin when approving)."""
        self.status = self.STATUS_ACTIVE
        self.posted_at = timezone.now()
        self.save(update_fields=["status", "posted_at"])

    def set_ad(self, ad_start: timezone.datetime, ad_end: timezone.datetime, save=True):
        """Set product as active ad for the provided interval."""
        self.ad = True
        self.ad_start = ad_start
        self.ad_end = ad_end
        if save:
            self.save(update_fields=["ad", "ad_start", "ad_end"])

    def expire_ad_if_needed(self):
        """Check and expire ad when ad_end passed. Call from periodic task or on admin views if you want immediate cleanup."""
        if self.ad and self.ad_end and timezone.now() > self.ad_end:
            self.ad = False
            self.ad_start = None
            self.ad_end = None
            self.save(update_fields=["ad", "ad_start", "ad_end"])

    def is_current_ad(self):
        """True if product currently within ad interval."""
        if not self.ad:
            return False
        now = timezone.now()
        if self.ad_start and now < self.ad_start:
            return False
        if self.ad_end and now > self.ad_end:
            return False
        return True

    def __str__(self):
        return self.name_ar or f"Product {self.pk}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    url = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        # On create, if an image file is present and no URL yet, upload to Cloudinary
        if self.image and not self.url:
            upload_result = cloudinary.uploader.upload(self.image)
            self.url = upload_result.get("secure_url")
            # Remove local file to avoid storing media on disk
            try:
                self.image.delete(save=False)
            except Exception:
                pass
            self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name_ar or self.product.pk}"


class AdRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ad_requests")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ad_requests")
    created_at = models.DateTimeField(auto_now_add=True)

    # admin decision fields
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_ad_requests")
    approved_at = models.DateTimeField(null=True, blank=True)

    # admin can set ad interval when approving
    ad_start = models.DateTimeField(null=True, blank=True)
    ad_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "product")

    def approve(self, admin_user, ad_start: timezone.datetime, ad_end: timezone.datetime):
        """Mark this AdRequest approved and activate ad on product."""
        self.is_approved = True
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.ad_start = ad_start
        self.ad_end = ad_end
        self.save(update_fields=["is_approved", "approved_by", "approved_at", "ad_start", "ad_end"])

        # set product ad fields
        product = self.product
        product.set_ad(ad_start=ad_start, ad_end=ad_end)

    def __str__(self):
        return f"{self.user.full_name_en if hasattr(self.user, 'full_name_en') else self.user} requested Ad for {self.product.name_ar}"
