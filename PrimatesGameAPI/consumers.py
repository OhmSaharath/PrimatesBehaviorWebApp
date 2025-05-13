import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RPiConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.rpi_num = self.scope['url_route']['kwargs']['rpi_num']
        self.group_name = f"rpi_{self.rpi_num}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Called by channel_layer.group_send
    async def state_update(self, event):
        data = event['data']
        # Send JSON to WebSocket
        await self.send(text_data=json.dumps(data))