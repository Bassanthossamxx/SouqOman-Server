from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer , OTPRequestSerializer, OTPVerifySerializer

from django.shortcuts import get_object_or_404

from .models import PhoneVerification, User
from core.utils import create_otp_transaction, activate_otp_transaction, verify_otp


class SendOTPView(APIView):
    """Step 1: Create and activate Akedly OTP transaction."""

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        # if not phone.startswith("+968"):
        #     return Response({"error": "Only Omani phone numbers are supported."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if record exists
        record, _ = PhoneVerification.objects.get_or_create(phone=phone)

        try:
            transaction_id = create_otp_transaction(phone)
            request_id = activate_otp_transaction(transaction_id)

            record.transaction_id = transaction_id
            record.request_id = request_id
            record.verified = False
            record.save()

            return Response(
                {"message": f"OTP sent successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """Step 2: Verify the OTP entered by the user."""

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        record = get_object_or_404(PhoneVerification, phone=phone)

        success, data = verify_otp(record.request_id, otp)
        if success:
            record.verified = True
            record.save()
            return Response({"message": "Phone verified successfully."}, status=status.HTTP_200_OK)
        return Response({"error": data}, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    """Resend OTP using the same Akedly transaction, with 60s cooldown."""

    def post(self, request):
        phone = request.data.get("phone")

        if not phone:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        # if not phone.startswith("+968"):
        #     return Response({"error": "Only Omani phone numbers are supported."}, status=status.HTTP_400_BAD_REQUEST)

        record = get_object_or_404(PhoneVerification, phone=phone)

        # 60-second cooldown
        if not record.can_resend():
            return Response(
                {"error": "Please wait 60 seconds before requesting another OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            new_request_id = activate_otp_transaction(record.transaction_id)
            record.request_id = new_request_id
            record.verified = False
            record.save()

            return Response(
                {"message": f"OTP resent successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AkedlyCallbackView(APIView):
    """Handle callback from Akedly with authentication data."""

    def post(self, request):
        data = request.data
        phone = data.get("verificationAddress", {}).get("phoneNumber")
        status_value = data.get("status")

        if phone and status_value == "success":
            PhoneVerification.objects.update_or_create(
                phone=phone,
                defaults={"verified": True, "transaction_id": data.get("transactionID")},
            )
        return Response({"message": "Callback received."}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """Step 3: Register user only if verified."""

    def post(self, request):
        phone = request.data.get("phone")

        # Ensure phone is verified
        verification = PhoneVerification.objects.filter(phone=phone, verified=True).first()
        if not verification:
            return Response(
                {"error": "Phone not verified. Please verify before registration."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # (optional) Mark verification as used
            verification.delete()

            return Response(
                {
                    "message": "User registered successfully.",
                    "access": str(access),
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    # Rate limiting scope
    throttle_scope = "auth_login"

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            return Response(
                {
                    "message": "User logged in successfully.",
                    "access": str(access),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    # Rate limiting scope
    throttle_scope = "auth_logout"

    def post(self, request):
        try:
            refresh_token_str = request.data.get("refresh")
            if not refresh_token_str:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            refresh_token = RefreshToken(refresh_token_str)

            try:
                outstanding_token = OutstandingToken.objects.get(
                    token=str(refresh_token),
                    user=request.user
                )
                if BlacklistedToken.objects.filter(token=outstanding_token).exists():
                    return Response({"detail": "Already logged out."}, status=status.HTTP_200_OK)

                BlacklistedToken.objects.create(token=outstanding_token)

            except OutstandingToken.DoesNotExist:
                refresh_token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# JWT endpoints with throttling scopes
class TokenObtainPairThrottledView(TokenObtainPairView):
    throttle_scope = "auth_token_obtain"


class TokenRefreshThrottledView(TokenRefreshView):
    throttle_scope = "auth_token_refresh"

