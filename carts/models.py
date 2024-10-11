from django.db import models
from store.models import Product, Variation
from accounts.models import Accounts

class Cart(models.Model):
    """Modelo para almacenar carritos de usuarios no autenticados."""
    cart_id = models.CharField(max_length=250, blank=True, unique=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Cart {self.cart_id}'

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'


class CartItem(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        """Calcula el subtotal del ítem (precio * cantidad)."""
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    class Meta:
        verbose_name = 'Ítem del carrito'
        verbose_name_plural = 'Ítems del carrito'
        ordering = ['product']
