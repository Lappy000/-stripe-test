"""
Models for the payments application.
Includes Item, Order, Discount, and Tax models.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Discount(models.Model):
    """
    Discount model that can be applied to Orders.
    Maps to Stripe Coupon/Discount.
    """
    name = models.CharField(max_length=255)
    percent_off = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Discount percentage (e.g., 10.00 for 10%)"
    )
    stripe_coupon_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.percent_off}%)"
    
    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"


class Tax(models.Model):
    """
    Tax model that can be applied to Orders.
    Maps to Stripe Tax Rate.
    """
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Tax percentage (e.g., 20.00 for 20%)"
    )
    inclusive = models.BooleanField(
        default=False,
        help_text="Whether the tax is included in the price"
    )
    stripe_tax_rate_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
    
    class Meta:
        verbose_name = "Tax"
        verbose_name_plural = "Taxes"


class Item(models.Model):
    """
    Product Item model with support for multiple currencies.
    """
    CURRENCY_CHOICES = [
        ('usd', 'USD - US Dollar'),
        ('eur', 'EUR - Euro'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='usd'
    )
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency.upper()}"
    
    @property
    def price_in_cents(self):
        """Return price in cents for Stripe API."""
        return int(self.price * 100)
    
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"


class Order(models.Model):
    """
    Order model that can contain multiple Items with optional Discount and Tax.
    """
    items = models.ManyToManyField(Item, through='OrderItem', related_name='orders')
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id}"
    
    @property
    def total_price(self):
        """Calculate total price of all items in the order."""
        total = sum(
            order_item.item.price * order_item.quantity
            for order_item in self.order_items.all()
        )
        return total
    
    @property
    def total_price_in_cents(self):
        """Return total price in cents for Stripe API."""
        return int(self.total_price * 100)
    
    @property
    def currency(self):
        """Get the currency from the first item in the order."""
        first_item = self.order_items.first()
        if first_item:
            return first_item.item.currency
        return 'usd'
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"


class OrderItem(models.Model):
    """
    Through model for Order-Item relationship with quantity.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity}x {self.item.name} in Order #{self.order.id}"
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        unique_together = ['order', 'item']
