from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Stocks(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    short_description = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    discount_coefficient = models.DecimalField(max_digits=3, decimal_places=2,
                                               validators=[MinValueValidator(Decimal('0.01')),
                                                           MaxValueValidator(Decimal('0.99'))])
    name_of_func_to_check = models.CharField(max_length=50)


class Shop(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)


class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True)
    promocode = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')


class Product(models.Model):
    class Meta:
        ordering = ["name", "price"]

    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    shops = models.ManyToManyField(Shop, through="ProductToShop")
    shopping_cart = models.ManyToManyField(ShoppingCart, through="ProductToShoppingCart", related_name="products")
    orders = models.ManyToManyField(Order, through="ProductToOrder", related_name="products")

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"


class ProductToOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    count = models.PositiveSmallIntegerField()


class ProductToShop(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    count = models.PositiveSmallIntegerField()


class ProductToShoppingCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    shopping_card = models.ForeignKey(ShoppingCart, on_delete=models.PROTECT)
    count = models.PositiveSmallIntegerField()



