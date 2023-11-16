from django.contrib.auth.forms import UserCreationForm 
from .models import User
from django import forms
 
class UserRegistrationForm(UserCreationForm):
 
    class Meta:
        
        model = User
        fields = ("email", 'first_name', 'last_name')
   

    
    def save(self, commit: bool = True) -> User:
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
 
        return User.objects.create_user(first_name, last_name, email, password, commit=commit)