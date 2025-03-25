from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('email/', views.handle_incoming_email, name='handle_incoming_email'),
]
