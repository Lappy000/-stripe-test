"""
Management command to load sample data for testing.
"""
from django.core.management.base import BaseCommand
from payments.models import Item, Order, OrderItem, Discount, Tax


class Command(BaseCommand):
    help = 'Load sample data for testing the Stripe integration'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create sample items in USD
        item1, _ = Item.objects.update_or_create(
            id=1,
            defaults={
                'name': 'Premium T-Shirt',
                'description': 'High-quality cotton t-shirt with modern design. Perfect for everyday wear.',
                'price': 29.99,
                'currency': 'usd',
            }
        )
        
        item2, _ = Item.objects.update_or_create(
            id=2,
            defaults={
                'name': 'Wireless Headphones',
                'description': 'Bluetooth 5.0 headphones with active noise cancellation and 30-hour battery life.',
                'price': 149.99,
                'currency': 'usd',
            }
        )
        
        item3, _ = Item.objects.update_or_create(
            id=3,
            defaults={
                'name': 'Smart Watch',
                'description': 'Feature-rich smartwatch with health monitoring, GPS, and water resistance.',
                'price': 299.99,
                'currency': 'usd',
            }
        )
        
        # Create sample items in EUR
        item4, _ = Item.objects.update_or_create(
            id=4,
            defaults={
                'name': 'Leather Wallet',
                'description': 'Genuine leather wallet with RFID protection. Handcrafted in Europe.',
                'price': 49.99,
                'currency': 'eur',
            }
        )
        
        item5, _ = Item.objects.update_or_create(
            id=5,
            defaults={
                'name': 'Designer Sunglasses',
                'description': 'Premium polarized sunglasses with UV400 protection.',
                'price': 129.99,
                'currency': 'eur',
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Item.objects.count()} items'))
        
        # Create sample discounts
        discount1, _ = Discount.objects.update_or_create(
            id=1,
            defaults={
                'name': 'Summer Sale',
                'percent_off': 10.00,
            }
        )
        
        discount2, _ = Discount.objects.update_or_create(
            id=2,
            defaults={
                'name': 'VIP Discount',
                'percent_off': 20.00,
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Discount.objects.count()} discounts'))
        
        # Create sample taxes
        tax1, _ = Tax.objects.update_or_create(
            id=1,
            defaults={
                'name': 'VAT',
                'percentage': 20.00,
                'inclusive': False,
            }
        )
        
        tax2, _ = Tax.objects.update_or_create(
            id=2,
            defaults={
                'name': 'Sales Tax',
                'percentage': 8.50,
                'inclusive': False,
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created {Tax.objects.count()} taxes'))
        
        # Create sample orders
        order1, created = Order.objects.update_or_create(
            id=1,
            defaults={
                'discount': discount1,
                'tax': tax2,
            }
        )
        if created:
            OrderItem.objects.create(order=order1, item=item1, quantity=2)
            OrderItem.objects.create(order=order1, item=item2, quantity=1)
        
        order2, created = Order.objects.update_or_create(
            id=2,
            defaults={
                'discount': discount2,
                'tax': None,
            }
        )
        if created:
            OrderItem.objects.create(order=order2, item=item3, quantity=1)
        
        order3, created = Order.objects.update_or_create(
            id=3,
            defaults={
                'discount': None,
                'tax': tax1,
            }
        )
        if created:
            OrderItem.objects.create(order=order3, item=item4, quantity=1)
            OrderItem.objects.create(order=order3, item=item5, quantity=1)
        
        self.stdout.write(self.style.SUCCESS(f'Created {Order.objects.count()} orders'))
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
