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
    path('games/<int:game_id>/rounds/', views.game_rounds, name='game_rounds'),
    path('games/<int:game_id>/create-round/', views.create_new_round, name='create_new_round'),
    path('rounds/<int:round_id>/close/', views.close_round, name='close_round'),
    path('rounds/<int:round_id>/select-winner/', views.select_winner, name='select_winner'),
    
    # Transactions
    path('transactions/', views.transactions_list, name='transactions_list'),
]
