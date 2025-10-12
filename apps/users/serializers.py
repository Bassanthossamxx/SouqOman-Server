from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "phone",
            "email",
            "password",
            "password2",
            "full_name_ar",
            "full_name_en",
            "governorate",
            "wilayat",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "full_name_ar": {"required": True},
            "full_name_en": {"required": True},
            "governorate": {"required": True},
            "wilayat": {"required": True},
        }

    def validate(self, attrs):
        # Check password match
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"passwords": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)

        # Run model clean() enforce governorate , wilayat validation
        try:
            user.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        user = authenticate(username=phone, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone or password.")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
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
        ]

class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)