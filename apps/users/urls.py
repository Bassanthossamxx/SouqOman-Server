from django.urls import path
from .views import RegisterView , LoginSerializer

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginSerializer.as_view(), name="login"),

]