import re

from django.core.exceptions import ValidationError


def validate_name_ar(value):
    if not re.match(r"^[\u0600-\u06FF\s0-9]+$", value):
        raise ValidationError("Full name Arabic must contain only Arabic letters, spaces, and English numbers.")


def validate_name_en(value):
    if not re.match(r"^[A-Za-z\s0-9]+$", value):
        raise ValidationError("Full name English must contain only English letters, spaces, and numbers.")


def validate_omani_phone(value):
    """
    Validates phone numbers for both Egyptian and Omani formats:
    - Egyptian: +20 followed by 10 digits
    - Omani: +968 followed by 8 digits
    """
    egyptian_pattern = r"^\+20[0-9]{10}$"
    omani_pattern = r"^\+968[0-9]{8}$"

    if not (re.match(egyptian_pattern, value) or re.match(omani_pattern, value)):
        raise ValidationError("Phone must follow Egyptian format (+20XXXXXXXXXX) or Omani format (+968XXXXXXXX)")
