from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name of product', help_text="Enter the name of the product")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price', help_text="Enter the price of the product")
    description = models.TextField(verbose_name='Description', help_text="Enter the description of the product", blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, verbose_name='Quantity', help_text="Enter the quantity of the product")
    ingredients = models.TextField(verbose_name='Ingredients', blank=True, null=True, help_text="Enter the ingredients of the product")
    photo = models.ImageField(upload_to='products/photos/', verbose_name='Photo', help_text="Upload a photo of the product", blank=True, null=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']

    def __str__(self):
        return self.name