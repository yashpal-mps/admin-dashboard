from django.contrib import admin
from django.urls import path
from campaign.views import SendEmail

urlpatterns = [
     path('send', SendEmail, name='send-email'),
]
