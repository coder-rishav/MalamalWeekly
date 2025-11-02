from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Auth
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # Users
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/permissions/', views.manage_user_permissions, name='manage_user_permissions'),
    
    # Deposits
    path('deposits/', views.deposit_requests, name='deposit_requests'),
    path('deposits/<int:request_id>/approve/', views.approve_deposit, name='approve_deposit'),
    path('deposits/<int:request_id>/reject/', views.reject_deposit, name='reject_deposit'),
    
    # Withdrawals
    path('withdrawals/', views.withdrawal_requests, name='withdrawal_requests'),
    path('withdrawals/<int:request_id>/approve/', views.approve_withdrawal, name='approve_withdrawal'),
    path('withdrawals/<int:request_id>/reject/', views.reject_withdrawal, name='reject_withdrawal'),
    
    # Games
    path('games/', views.games_management, name='games_management'),
    path('games/create/', views.create_game, name='create_game'),
    path('games/<int:game_id>/edit/', views.edit_game, name='edit_game'),
    path('games/<int:game_id>/rounds/', views.game_rounds, name='game_rounds'),
    path('games/<int:game_id>/create-round/', views.create_new_round, name='create_new_round'),
    path('rounds/<int:round_id>/close/', views.close_round, name='close_round'),
    path('rounds/<int:round_id>/select-winner/', views.select_winner, name='select_winner'),
    
    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
    
    # Ban Appeals
    path('appeals/', views.ban_appeals_list, name='ban_appeals_list'),
    path('appeals/<int:appeal_id>/review/', views.review_appeal, name='review_appeal'),
    
    # Payment Gateways
    path('payment-gateways/', views.payment_gateways_list, name='payment_gateways_list'),
    path('payment-gateways/add/', views.add_payment_gateway, name='add_payment_gateway'),
    path('payment-gateways/<int:gateway_id>/edit/', views.edit_payment_gateway, name='edit_payment_gateway'),
    path('payment-gateways/<int:gateway_id>/toggle-status/', views.toggle_gateway_status, name='toggle_gateway_status'),
    path('payment-gateways/<int:gateway_id>/toggle-mode/', views.toggle_gateway_mode, name='toggle_gateway_mode'),
    path('payment-gateways/<int:gateway_id>/delete/', views.delete_payment_gateway, name='delete_payment_gateway'),
]
