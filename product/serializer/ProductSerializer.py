from rest_framework import serializers
from product.models.Product import Product

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'