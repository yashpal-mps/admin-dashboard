from django.contrib import admin
from product.models.Product import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'type', 'category', 'created_at', 'updated_at')
    list_filter = ('type', 'category', 'created_at')
    search_fields = ('name', 'description', 'category')
    ordering = ('-created_at',)
