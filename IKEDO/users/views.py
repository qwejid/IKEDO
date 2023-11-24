from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse
from .forms import CustomAuthenticationForm, UserRegistrationForm

class UserRegistration(CreateView):
    template_name = "reg2.html"
    form_class = UserRegistrationForm
 
    def get_success_url(self):
       return reverse("login")
    
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "login2.html"
    

    


