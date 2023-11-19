from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import validate_email

class CustomUserManager(UserManager):
 
    def _get_email(self, email: str):
        validate_email(email)
        return self.normalize_email(email)
 
    def _create_user(
        self,
        first_name: str,
        last_name: str,  
        email: str, 
        password: str,                
        commit: bool,
        is_staff: bool = False, 
        is_superuser: bool = False,  
        token: str = None,      
    ):         
        email = self._get_email(email)         
        user = User(first_name=first_name, last_name=last_name, email=email, username=email, is_staff=is_staff, is_superuser=is_superuser, token=token)
        user.set_password(password)
         
        if commit:
            user.save()
             
        return user
 
    def create_superuser(self, first_name: str, last_name: str, email: str, password: str, token: str = None, commit: bool = True):
        return self._create_user(first_name, last_name, email, password, is_staff=True, is_superuser=True, token=token, commit=commit)
 
    def create_user(self, first_name: str, last_name: str, email: str, password: str, commit: bool = True):
        return self._create_user(first_name, last_name, email, password, commit=commit)
 
class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=30, blank=True, verbose_name='Имя')  
    last_name = models.CharField(max_length=30, blank=True, verbose_name='Фамилия')   
    token = models.CharField(max_length=433, blank=True, null=True, verbose_name='Токен')  # Новое поле для токена
    
    USERNAME_FIELD = "email" 
    REQUIRED_FIELDS = ["first_name", "last_name", "token"]
    objects = CustomUserManager()
    
    

# мой
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZGJjOWUwZC0zNDg2LTRkNTAtOWYyYy0yMTYxZjc2ZWY0NzUiLCJnaXZlbl9uYW1lIjoi0JzQuNGF0LDQuNC7IiwiZmFtaWx5X25hbWUiOiLQqNC40YjQutC40L0iLCJ2ZXJzaW9uIjoidjEiLCJtaWRkbGVfbmFtZSI6ItCV0LLQs9C10L3RjNC10LLQuNGHIiwidG9rZW5fdHlwZSI6IjMiLCJuYmYiOjE3MDAxMjcwNzAsImV4cCI6MTczMTc0NzM1MCwiaXNzIjoiYXBpLWd3LmtlZG8tZGVtby5jbG91ZC5hc3RyYWwtZGV2LnJ1IiwiYXVkIjoia2VkbyJ9.7Urqx-_Ht_ybtOZ9wfIDgzX1qy7_wYa7_sV347WLuME

# дима
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjNjllOWIwYS0xYzg0LTQ0YmYtYTRmYy01OTY4NGM3ZDMyZTciLCJnaXZlbl9uYW1lIjoi0JDQu9C10LrRgdC10LkiLCJmYW1pbHlfbmFtZSI6ItCY0LLQsNC90L7QsiIsInZlcnNpb24iOiJ2MSIsIm1pZGRsZV9uYW1lIjoi0JDQvdC00YDQtdC10LLQuNGHIiwidG9rZW5fdHlwZSI6IjMiLCJuYmYiOjE3MDAzOTU2MjcsImV4cCI6MTczMjAxNzk3MywiaXNzIjoiYXBpLWd3LmtlZG8tZGVtby5jbG91ZC5hc3RyYWwtZGV2LnJ1IiwiYXVkIjoia2VkbyJ9.qlrbvVxd75hkR-wQ5dgqIeb-MNtvgZWgMiNX_kawUzg