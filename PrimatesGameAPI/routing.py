from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # matches ws://<host>/ws/rpi-states/1/
    re_path(r'ws/rpi-states/(?P<rpi_num>\d+)/$', consumers.RPiConsumer.as_asgi()),
]