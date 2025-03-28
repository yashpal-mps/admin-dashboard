from django.db import models
from product.models.Product import Product
from agent.models.Agent import Agent

# Create your models here.
class Campaign(models.Model):
    name = models.CharField(max_length=255)  
    description = models.TextField() 
    products = models.ManyToManyField(Product, related_name="campaigns")
    agent_name = models.ForeignKey(Agent, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name