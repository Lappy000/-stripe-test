"""
URL configuration for payments application.
"""
from django.urls import path
from .views import (
    HomeView,
    ItemDetailView,
    BuyItemView,
    OrderDetailView,
    BuyOrderView,
    PaymentIntentItemView,
    PaymentIntentPageView,
    SuccessView,
    CancelView,
)

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='home'),
    
    # Item endpoints
    path('item/<int:item_id>/', ItemDetailView.as_view(), name='item_detail'),
    path('buy/<int:item_id>/', BuyItemView.as_view(), name='buy_item'),
    
    # Order endpoints
    path('order/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('buy-order/<int:order_id>/', BuyOrderView.as_view(), name='buy_order'),
    
    # Payment Intent endpoints (bonus)
    path('item/<int:item_id>/intent/', PaymentIntentPageView.as_view(), name='payment_intent_page'),
    path('payment-intent/<int:item_id>/', PaymentIntentItemView.as_view(), name='payment_intent'),
    
    # Result pages
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
]
