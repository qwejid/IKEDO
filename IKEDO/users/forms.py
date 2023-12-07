from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from .models import User
from django import forms


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'login__input', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'login__input', 'placeholder': 'Password'})
    )
 

class UserRegistrationForm(UserCreationForm):
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'login__input', 'placeholder': 'Email'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'login__input', 'placeholder': 'Имя'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'login__input', 'placeholder': 'Фамилия'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'login__input', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'login__input', 'placeholder': 'Повторите пароль'}))
    
    class Meta:        
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def save(self, commit: bool = True) -> User:
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
 
        return User.objects.create_user(first_name, last_name, email, password, commit=commit)