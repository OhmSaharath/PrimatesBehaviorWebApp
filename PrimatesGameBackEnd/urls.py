
from django.urls import path , include
from . import views
from django.contrib.auth import views as authviews

app_name = 'backend'


urlpatterns = [
    path("rfid_response/", views.response_game_RFID, name="response_game_RFID"),
]