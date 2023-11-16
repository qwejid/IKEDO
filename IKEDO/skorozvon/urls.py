from django.urls import path 
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("up", views.update_token, name='update_token'),
    path("call", views.call, name='call'),

    
]
