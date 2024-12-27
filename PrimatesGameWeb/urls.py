from django.urls import path , include
from . import views
from django.contrib.auth import views as authviews

app_name = 'webapp'

urlpatterns = [
    path("", views.home, name="home"),
    path('profile/<username>', views.profile, name='profile'),
    path("register-primates/", views.primates, name="register-primates"),
    path("start-game/", views.start_game, name="start-game"),
    path("standby/", views.standby, name="standby"),
    path("game_logout/", views.close_games, name="game_logout"),
    path("get-game-config-form/", views.get_game_config_form, name="get_game_config_form"),
    path('reports/', views.report_page, name='reports'),
    path('generate_csv/', views.generate_csv, name='generate_csv'),
]