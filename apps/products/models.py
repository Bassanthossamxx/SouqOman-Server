from django.db import models

class Category(models.Model):
    name_en = models.CharField(max_length=255, unique=True)
    name_ar = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name_ar


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)

    class Meta:
        unique_together = [
            ("category", "name_ar"),
            ("category", "name_en"),
        ]

    def __str__(self):
        return f"{self.name_ar} ({self.category.name_ar})"
