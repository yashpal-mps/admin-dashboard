from django.db import models
from dashboard.models.Leads import Lead

# Create your models here.
class Conversation(models.Model):
    id = models.AutoField(primary_key=True)
    leads = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.message