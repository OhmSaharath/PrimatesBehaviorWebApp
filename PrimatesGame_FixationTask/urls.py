from django.urls import path , include
from PrimatesGame_FixationTask import views

app_name = 'fixation_game'

urlpatterns = [
    path('fixation/<int:gameinstance>',views.game_view, name='fixation-page'),
    path("fixation/signalresponse/<int:gameinstance>",views.fixationtask_signal_response, name="signalresponse"),
    path('fixation/get_game_config/<int:gameinstance>/', views.get_game_config, name='get_game_config'),
]