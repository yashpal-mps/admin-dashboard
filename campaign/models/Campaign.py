from django.db import models
from product.models.Product import Product
from agent.models.Agent import Agent


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
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
