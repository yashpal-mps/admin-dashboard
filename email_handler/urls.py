from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmailHandler.as_view(), name='email-handler'),
    path('send', views.SendEmailView.as_view(), name='send-email'),
]
