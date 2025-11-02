from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('games/', views.games_list, name='games_list'),
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    path('game/<int:game_id>/play/<int:round_id>/', views.play_game, name='play_game'),
    path('my-entries/', views.my_entries, name='my_entries'),
    path('winners/', views.winners_list, name='winners_list'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
