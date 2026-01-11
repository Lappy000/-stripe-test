"""
Views for the payments application.
Implements Stripe Checkout Session and Payment Intent functionality.
"""
import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import Item, Order


def get_stripe_keys(currency: str) -> tuple:
    """
    Get Stripe API keys based on currency.
    Returns (public_key, secret_key) tuple.
    """
    if currency.lower() == 'eur':
        return settings.STRIPE_PUBLIC_KEY_EUR, settings.STRIPE_SECRET_KEY_EUR
    return settings.STRIPE_PUBLIC_KEY_USD, settings.STRIPE_SECRET_KEY_USD


class ItemDetailView(View):
    """
    GET /item/{id}
    Returns HTML page with item details and Buy button.
    """
    
    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        public_key, _ = get_stripe_keys(item.currency)
        
        context = {
            'item': item,
            'stripe_public_key': public_key,
        }
        return render(request, 'payments/item_detail.html', context)


class BuyItemView(View):
    """
    GET /buy/{id}
    Creates Stripe Checkout Session for the item and returns session ID.
    """
    
    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        public_key, secret_key = get_stripe_keys(item.currency)
        
        stripe.api_key = secret_key
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': item.currency,
                        'product_data': {
                            'name': item.name,
                            'description': item.description,
                        },
                        'unit_amount': item.price_in_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.DOMAIN + '/success/',
                cancel_url=settings.DOMAIN + '/cancel/',
            )
            
            return JsonResponse({'id': session.id})
        
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)


class OrderDetailView(View):
    """
    GET /order/{id}
    Returns HTML page with order details and Pay button.
    """
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        public_key, _ = get_stripe_keys(order.currency)
        
        context = {
            'order': order,
            'stripe_public_key': public_key,
        }
        return render(request, 'payments/order_detail.html', context)


class BuyOrderView(View):
    """
    GET /buy-order/{id}
    Creates Stripe Checkout Session for the order with discount and tax.
    Returns session ID.
    """
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        public_key, secret_key = get_stripe_keys(order.currency)
        
        stripe.api_key = secret_key
        
        try:
            # Prepare line items from order items
            line_items = []
            tax_rates = []
            
            # Create or get tax rate in Stripe if tax exists
            if order.tax:
                if order.tax.stripe_tax_rate_id:
                    tax_rates = [order.tax.stripe_tax_rate_id]
                else:
                    # Create tax rate in Stripe
                    tax_rate = stripe.TaxRate.create(
                        display_name=order.tax.name,
                        percentage=float(order.tax.percentage),
                        inclusive=order.tax.inclusive,
                    )
                    order.tax.stripe_tax_rate_id = tax_rate.id
                    order.tax.save()
                    tax_rates = [tax_rate.id]
            
            for order_item in order.order_items.all():
                item_data = {
                    'price_data': {
                        'currency': order_item.item.currency,
                        'product_data': {
                            'name': order_item.item.name,
                            'description': order_item.item.description,
                        },
                        'unit_amount': order_item.item.price_in_cents,
                    },
                    'quantity': order_item.quantity,
                }
                
                if tax_rates:
                    item_data['tax_rates'] = tax_rates
                
                line_items.append(item_data)
            
            # Prepare session parameters
            session_params = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': settings.DOMAIN + '/success/',
                'cancel_url': settings.DOMAIN + '/cancel/',
            }
            
            # Add discount/coupon if exists
            if order.discount:
                if order.discount.stripe_coupon_id:
                    session_params['discounts'] = [{'coupon': order.discount.stripe_coupon_id}]
                else:
                    # Create coupon in Stripe
                    coupon = stripe.Coupon.create(
                        percent_off=float(order.discount.percent_off),
                        duration='once',
                        name=order.discount.name,
                    )
                    order.discount.stripe_coupon_id = coupon.id
                    order.discount.save()
                    session_params['discounts'] = [{'coupon': coupon.id}]
            
            session = stripe.checkout.Session.create(**session_params)
            
            return JsonResponse({'id': session.id})
        
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)


class PaymentIntentItemView(View):
    """
    GET /payment-intent/{id}
    Creates Stripe Payment Intent for the item.
    Returns client_secret for frontend processing.
    """
    
    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        public_key, secret_key = get_stripe_keys(item.currency)
        
        stripe.api_key = secret_key
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=item.price_in_cents,
                currency=item.currency,
                payment_method_types=['card'],
                metadata={
                    'item_id': item.id,
                    'item_name': item.name,
                },
            )
            
            return JsonResponse({
                'clientSecret': intent.client_secret,
                'publicKey': public_key,
            })
        
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)


class PaymentIntentPageView(View):
    """
    GET /item/{id}/intent
    Returns HTML page for Payment Intent flow.
    """
    
    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        public_key, secret_key = get_stripe_keys(item.currency)
        
        stripe.api_key = secret_key
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=item.price_in_cents,
                currency=item.currency,
                payment_method_types=['card'],
                metadata={
                    'item_id': item.id,
                    'item_name': item.name,
                },
            )
            
            context = {
                'item': item,
                'stripe_public_key': public_key,
                'client_secret': intent.client_secret,
                'total': item.price,
                'discount': None,
                'tax': None,
                'discount_amount': 0,
                'tax_amount': 0,
            }
            return render(request, 'payments/payment_intent.html', context)
        
        except stripe.error.StripeError as e:
            # If error, render page without payment intent
            context = {
                'item': item,
                'stripe_public_key': public_key,
                'client_secret': '',
                'total': item.price,
                'discount': None,
                'tax': None,
                'discount_amount': 0,
                'tax_amount': 0,
            }
            return render(request, 'payments/payment_intent.html', context)


class SuccessView(View):
    """
    GET /success/
    Payment success page.
    """
    
    def get(self, request):
        return render(request, 'payments/success.html')


class CancelView(View):
    """
    GET /cancel/
    Payment cancelled page.
    """
    
    def get(self, request):
        return render(request, 'payments/cancel.html')


class HomeView(View):
    """
    GET /
    Home page with list of all items and orders.
    """
    
    def get(self, request):
        items = Item.objects.all()
        orders = Order.objects.all()
        
        context = {
            'items': items,
            'orders': orders,
        }
        return render(request, 'payments/home.html', context)
