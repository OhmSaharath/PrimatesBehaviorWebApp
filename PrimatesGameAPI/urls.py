
from django.urls import path 
from . import views 

app_name = 'api'

urlpatterns = [ 
    path('primates', views.PrimatesView.as_view() , name = 'primates'), 
    path('primates/<int:pk>', views.SinglePrimatesView.as_view()), 
    path('rpi-boards', views.RPiBoradsView.as_view()),
    path('rpi-boards/<int:pk>', views.SingleRPiBoardView.as_view()),
    path('rpi-states', views.RPiStatesView.as_view()),
    path('rpi-states/<int:pk>', views.SingleRPiStateViews.as_view()),
    path('games', views.GamesView.as_view()),
    path('games/<int:pk>', views.SingleGameView.as_view()),
    path('games-instances', views.GameInstancesView.as_view() , name = 'game-instance'),
    path('games-instances/<int:pk>', views.SingleGameInstanceView.as_view()),
    path('fixationconfigs', views.FixationGameConfigView.as_view() ,name = 'fixationconfigs'),
    path('fixationconfigs/<int:pk>', views.SingleFixationGameConfigView.as_view()),
    path('groups/researcher/users', views.ResercherGroupManangeView.as_view()),
    path('groups/researcher/users/<int:pk>', views.ResercherDeleteView.as_view()),
    
] 
