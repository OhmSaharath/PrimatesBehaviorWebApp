from django.urls import path , include
from PrimatesGame_FixationTask import views

app_name = 'fixation_game'

urlpatterns = [
    path('fixation/<int:gameinstance>',views.game_view, name='fixation-page'),
    #path("fixation/handle-signal/<int:gameinstance>",views.game_push_button_handle_signal, name="handle-signal"),
]