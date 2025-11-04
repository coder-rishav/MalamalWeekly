from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Transaction History
    path('history/', views.transaction_history, name='transaction_history'),
    
    # Add Credits (New Payment Integration)
    path('add-credits/', views.add_credits, name='add_credits'),
    path('create-payment-order/', views.create_payment_order, name='create_payment_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
    
    # Withdrawals
    path('withdraw/', views.withdraw_credits, name='withdraw_credits'),
    
    # Legacy/Admin Requests
    path('deposits/', views.deposit_requests, name='deposit_requests'),
    path('withdrawals/', views.withdrawal_requests, name='withdrawal_requests'),
    
    # Webhook Endpoints (for payment gateway callbacks)
    path('webhooks/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/payu/', views.payu_webhook, name='payu_webhook'),
]
