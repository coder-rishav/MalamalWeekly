from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('history/', views.transaction_history, name='transaction_history'),
    path('add-credits/', views.add_credits, name='add_credits'),
    path('withdraw/', views.withdraw_credits, name='withdraw_credits'),
    path('deposits/', views.deposit_requests, name='deposit_requests'),
    path('withdrawals/', views.withdrawal_requests, name='withdrawal_requests'),
]
