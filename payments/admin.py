"""
Django Admin configuration for payments models.
"""
from django.contrib import admin
from .models import Item, Order, OrderItem, Discount, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin interface for Item model."""
    list_display = ['id', 'name', 'price', 'currency', 'description_short']
    list_filter = ['currency']
    search_fields = ['name', 'description']
    ordering = ['id']
    
    def description_short(self, obj):
        """Return truncated description."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """Admin interface for Discount model."""
    list_display = ['id', 'name', 'percent_off', 'stripe_coupon_id']
    search_fields = ['name']
    ordering = ['id']


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """Admin interface for Tax model."""
    list_display = ['id', 'name', 'percentage', 'inclusive', 'stripe_tax_rate_id']
    list_filter = ['inclusive']
    search_fields = ['name']
    ordering = ['id']


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem in Order admin."""
    model = OrderItem
    extra = 1
    min_num = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""
    list_display = ['id', 'get_items_count', 'total_price', 'currency', 'discount', 'tax', 'created_at']
    list_filter = ['discount', 'tax', 'created_at']
    search_fields = ['id']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    def get_items_count(self, obj):
        """Return count of items in order."""
        return obj.order_items.count()
    get_items_count.short_description = 'Items Count'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model."""
    list_display = ['id', 'order', 'item', 'quantity']
    list_filter = ['order']
    search_fields = ['item__name']
    ordering = ['order', 'item']
