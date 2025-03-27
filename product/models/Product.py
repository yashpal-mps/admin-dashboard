from django.db import models

from django.db import models

from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    type = models.CharField(max_length=10)
    category = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name