import re

from django.core.exceptions import ValidationError


def validate_name_ar(value):
    if not re.match(r"^[\u0600-\u06FF\s0-9]+$", value):
        raise ValidationError("Full name Arabic must contain only Arabic letters, spaces, and English numbers.")


def validate_name_en(value):
    if not re.match(r"^[A-Za-z\s0-9]+$", value):
        raise ValidationError("Full name English must contain only English letters, spaces, and numbers.")


def validate_omani_phone(value):
    # Must start with +968 followed by 8 digits
    if not re.match(r"^\+968[0-9]{8}$", value):
        raise ValidationError("Phone must follow Omani format: +968XXXXXXXX")
