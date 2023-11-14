from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", views.UserRegistration.as_view(), name="user_registration"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout")
]