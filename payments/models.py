"""
Models for the payments application.
Includes Item, Order, Discount, and Tax models.
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Discount(models.Model):
    """
    Модель скидки для заказов.
    Соответствует Stripe Coupon/Discount.
    """
    name = models.CharField(max_length=255, verbose_name="Название")
    percent_off = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Процент скидки",
        help_text="Процент скидки (например, 10.00 для 10%)"
    )
    stripe_coupon_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.percent_off}%)"
    
    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"


class Tax(models.Model):
    """
    Модель налога для заказов.
    Соответствует Stripe Tax Rate.
    """
    name = models.CharField(max_length=255, verbose_name="Название")
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Процент налога",
        help_text="Процент налога (например, 20.00 для 20%)"
    )
    inclusive = models.BooleanField(
        default=False,
        verbose_name="Включён в цену",
        help_text="Налог уже включён в стоимость товара"
    )
    stripe_tax_rate_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
    
    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"


class Item(models.Model):
    """
    Product Item model with support for multiple currencies.
    """
    CURRENCY_CHOICES = [
        ('usd', 'USD - Доллар США'),
        ('eur', 'EUR - Евро'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Цена"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='usd',
        verbose_name="Валюта"
    )
    image = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Изображение",
        help_text="Имя файла изображения в папке img (например: smartwatch.jpg)"
    )
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency.upper()}"
    
    @property
    def price_in_cents(self):
        """Return price in cents for Stripe API."""
        return int(self.price * 100)
    
    @property
    def image_url(self):
        """Return the URL for the item image."""
        if self.image:
            return f"/static/img/{self.image}"
        return None
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


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
