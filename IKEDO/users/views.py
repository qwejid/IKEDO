from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse
 
from .forms import UserRegistrationForm
 
class UserRegistration(CreateView):
    template_name = "user_registration.html"
    form_class = UserRegistrationForm
 
    def get_success_url(self):
       return reverse("login")
    
class Login(LoginView):
    template_name = "login.html"


