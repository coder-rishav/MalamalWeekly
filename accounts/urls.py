from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/currency/', views.change_currency, name='change_currency'),
    path('kyc/submit/', views.submit_kyc, name='submit_kyc'),
    path('kyc/view/', views.view_kyc, name='view_kyc'),
    path('banned/', views.account_banned, name='account_banned'),
]
