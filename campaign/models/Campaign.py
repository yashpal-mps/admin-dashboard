from django.db import models
from product.models.Product import Product
from agent.models.Agent import Agent
from datetime import timedelta, time


class Campaign(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    products = models.ManyToManyField(Product, related_name="campaigns")
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="campaigns")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    send_start_time = models.TimeField(
        default=time(18, 0),  # 6:00 PM
        help_text="Daily start time for sending emails"
    )
    send_end_time = models.TimeField(
        default=time(22, 0),  # 10:00 PM
        help_text="Daily end time for sending emails"
    )
    emails_per_hour = models.IntegerField(
        default=10,
        help_text="Maximum number of emails to send per hour"
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
