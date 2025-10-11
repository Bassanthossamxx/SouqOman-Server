from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    # Rate limiting scope (see REST_FRAMEWORK.DEFAULT_THROTTLE_RATES)
    throttle_scope = "auth_register"

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #add tokens immediately so the user is authenticated right after registration
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
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
